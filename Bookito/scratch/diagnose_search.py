"""
Diagnostic script: Two tests for improving vector search quality.

Test 1: Require ALL concept words to match in vector search results (stemmed matching).
Test 2: Adaptive score threshold using statistical elbow detection.
"""
import os
import sys
import re
import math
import statistics
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.query_manager import QueryManager, DEFAULT_TOP_K
from processors.augmented_content_generator import (
    is_valid_syntactic_match,
    DEFAULT_INITIAL_PAGE,
)

# ---- Test Configuration ----
CONCEPTS = [
    "business processes",
    "distributed workflow engine",
    "capable of executing business",
    "different workflow execution models",
    "version upgrades",
    "human approval steps",
    "duplicate messages",
    "feature design document",
    "parallel branches",
    "several weeks"
]

TOP_K = 100
SNOWBALL_STEMMER_LANGUAGE = "english"
MATCH_TYPE_SYNTACTIC = "syntactic"
MATCH_TYPE_SEMANTIC = "semantic"
RESULT_KEY_SCORE = "score"
RESULT_KEY_CHUNK_TEXT = "chunk_text"
RESULT_KEY_BOOK_ID = "book_id"
RESULT_KEY_CHUNK_INDEX = "chunk_index"

# Score threshold approach: Median Absolute Deviation (MAD) based
# We keep scores above: median - k * MAD, where k controls sensitivity
# This is more robust to outliers than mean/stddev
MAD_SENSITIVITY_FACTOR = 1.0


def compute_adaptive_threshold(scores: list[float]) -> tuple[float, dict]:
    """Computes an adaptive score threshold using a combined approach:

    1. Compute the median and MAD (Median Absolute Deviation) of scores.
    2. Compute the 'elbow' point: find the largest relative gap in sorted scores.
    3. Take the HIGHER of the two thresholds (more conservative).

    Returns the threshold and a dict of diagnostic info.
    """
    if not scores:
        return 0.0, {}

    sorted_desc = sorted(scores, reverse=True)
    n = len(sorted_desc)

    # --- Method A: Median + MAD ---
    median_val = statistics.median(sorted_desc)
    deviations = [abs(s - median_val) for s in sorted_desc]
    mad = statistics.median(deviations)
    mad_threshold = median_val + mad * MAD_SENSITIVITY_FACTOR

    # --- Method B: Elbow/Knee detection ---
    # Find the point where consecutive score drops are largest relative to range
    elbow_threshold = sorted_desc[-1]  # fallback: keep everything
    if n >= 3:
        gaps = []
        for i in range(n - 1):
            gap = sorted_desc[i] - sorted_desc[i + 1]
            gaps.append((gap, i, sorted_desc[i + 1]))

        # Find the gap that is significantly above the mean gap
        mean_gap = sum(g[0] for g in gaps) / len(gaps)
        std_gap = (sum((g[0] - mean_gap) ** 2 for g in gaps) / len(gaps)) ** 0.5

        # The elbow is the first gap that exceeds mean + 1.5*stddev
        elbow_gap_threshold = mean_gap + 1.5 * std_gap
        for gap_val, idx, score_below in gaps:
            if gap_val > elbow_gap_threshold and idx >= 2:
                # Set threshold just above the score below the gap
                elbow_threshold = score_below + (gap_val * 0.1)
                break

    # Take the more conservative (higher) threshold
    final_threshold = max(mad_threshold, elbow_threshold)

    diagnostics = {
        "max_score": sorted_desc[0] if sorted_desc else 0,
        "min_score": sorted_desc[-1] if sorted_desc else 0,
        "median": median_val,
        "mad": mad,
        "mad_threshold": mad_threshold,
        "elbow_threshold": elbow_threshold,
        "final_threshold": final_threshold,
        "total_results": n,
    }
    return final_threshold, diagnostics


def run_test_1(qm, stemmer):
    """Test 1: Require ALL concept words to appear in vector search results (stemmed matching)."""
    print("=" * 90)
    print("TEST 1: Require ALL concept words to match in vector search results")
    print("=" * 90)
    print()

    total_vec_returned = 0
    total_vec_kept = 0
    total_vec_rejected = 0
    total_lex_returned = 0
    total_lex_kept = 0
    all_books = set()

    for concept in CONCEPTS:
        vec_results = qm.vector_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)
        lex_results = qm.lexical_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)

        vec_kept = 0
        vec_rejected = 0
        vec_books = set()

        for r in vec_results:
            chunk_text = r.get(RESULT_KEY_CHUNK_TEXT, "")
            if is_valid_syntactic_match(concept, chunk_text, stemmer):
                vec_kept += 1
                vec_books.add(r.get(RESULT_KEY_BOOK_ID))
            else:
                vec_rejected += 1

        lex_kept = 0
        lex_books = set()
        for r in lex_results:
            chunk_text = r.get(RESULT_KEY_CHUNK_TEXT, "")
            if is_valid_syntactic_match(concept, chunk_text, stemmer):
                lex_kept += 1
                lex_books.add(r.get(RESULT_KEY_BOOK_ID))

        combined_books = vec_books | lex_books
        all_books.update(combined_books)

        total_vec_returned += len(vec_results)
        total_vec_kept += vec_kept
        total_vec_rejected += vec_rejected
        total_lex_returned += len(lex_results)
        total_lex_kept += lex_kept

        print(f"  [{concept}]")
        print(f"    Vector: {len(vec_results)} returned -> {vec_kept} kept, {vec_rejected} rejected")
        print(f"    Lexical: {len(lex_results)} returned -> {lex_kept} kept")
        print(f"    Unique books (combined): {len(combined_books)}")

    print()
    print(f"  TOTALS:")
    print(f"    Vector:  {total_vec_returned} returned -> {total_vec_kept} kept, {total_vec_rejected} rejected")
    print(f"    Lexical: {total_lex_returned} returned -> {total_lex_kept} kept")
    print(f"    Total unique books: {len(all_books)}")
    print()
    return all_books


def run_test_2(qm, stemmer):
    """Test 2: Adaptive score threshold using statistical methods."""
    print("=" * 90)
    print("TEST 2: Adaptive score threshold (Median+MAD / Elbow detection)")
    print("=" * 90)
    print()

    total_vec_returned = 0
    total_vec_kept = 0
    total_vec_rejected = 0
    total_lex_returned = 0
    total_lex_kept = 0
    all_books = set()

    for concept in CONCEPTS:
        vec_results = qm.vector_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)
        lex_results = qm.lexical_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)

        # --- Apply adaptive threshold to VECTOR results ---
        vec_scores = [r.get(RESULT_KEY_SCORE, 0.0) for r in vec_results]
        threshold, diag = compute_adaptive_threshold(vec_scores)

        vec_kept = 0
        vec_rejected = 0
        vec_books = set()
        vec_kept_scores = []

        for r in vec_results:
            score = r.get(RESULT_KEY_SCORE, 0.0)
            if score >= threshold:
                vec_kept += 1
                vec_books.add(r.get(RESULT_KEY_BOOK_ID))
                vec_kept_scores.append(score)
            else:
                vec_rejected += 1

        # --- Apply adaptive threshold to LEXICAL results ---
        lex_scores = [r.get(RESULT_KEY_SCORE, 0.0) for r in lex_results]
        lex_threshold, lex_diag = compute_adaptive_threshold(lex_scores)

        lex_kept = 0
        lex_books = set()
        for r in lex_results:
            score = r.get(RESULT_KEY_SCORE, 0.0)
            if score >= lex_threshold:
                lex_kept += 1
                lex_books.add(r.get(RESULT_KEY_BOOK_ID))

        combined_books = vec_books | lex_books
        all_books.update(combined_books)

        total_vec_returned += len(vec_results)
        total_vec_kept += vec_kept
        total_vec_rejected += vec_rejected
        total_lex_returned += len(lex_results)
        total_lex_kept += lex_kept

        print(f"  [{concept}]")
        if diag:
            print(f"    Vector scores: max={diag['max_score']:.4f}, min={diag['min_score']:.4f}, median={diag['median']:.4f}")
            print(f"    Vector MAD threshold={diag['mad_threshold']:.4f}, elbow threshold={diag['elbow_threshold']:.4f}")
            print(f"    Vector FINAL threshold={diag['final_threshold']:.4f}")
        print(f"    Vector: {len(vec_results)} returned -> {vec_kept} kept, {vec_rejected} rejected")
        if vec_kept_scores:
            print(f"    Vector kept score range: [{min(vec_kept_scores):.4f}, {max(vec_kept_scores):.4f}]")
        if lex_diag:
            print(f"    Lexical scores: max={lex_diag['max_score']:.4f}, min={lex_diag['min_score']:.4f}, median={lex_diag['median']:.4f}")
            print(f"    Lexical FINAL threshold={lex_diag['final_threshold']:.4f}")
        print(f"    Lexical: {len(lex_results)} returned -> {lex_kept} kept")
        print(f"    Unique books (combined): {len(combined_books)}")

    print()
    print(f"  TOTALS:")
    print(f"    Vector:  {total_vec_returned} returned -> {total_vec_kept} kept, {total_vec_rejected} rejected")
    print(f"    Lexical: {total_lex_returned} returned -> {total_lex_kept} kept")
    print(f"    Total unique books: {len(all_books)}")
    print()
    return all_books


def main():
    qm = QueryManager()
    stemmer = SnowballStemmer(SNOWBALL_STEMMER_LANGUAGE)

    print()
    print("Concepts being tested:")
    for i, c in enumerate(CONCEPTS, 1):
        print(f"  {i}. {c}")
    print()

    # --- Baseline ---
    print("=" * 90)
    print("BASELINE: Current behavior (no additional filtering on vector results)")
    print("=" * 90)
    baseline_books = set()
    baseline_total_hits = 0
    for concept in CONCEPTS:
        vec = qm.vector_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)
        lex = qm.lexical_search(concept, DEFAULT_INITIAL_PAGE, TOP_K, TOP_K)
        for r in vec + lex:
            baseline_books.add(r.get(RESULT_KEY_BOOK_ID))
        baseline_total_hits += len(vec) + len(lex)
    print(f"  Total raw hits (vec + lex, all concepts): {baseline_total_hits}")
    print(f"  Total unique books: {len(baseline_books)}")
    print()

    # --- Test 1 ---
    test1_books = run_test_1(qm, stemmer)

    # --- Test 2 ---
    test2_books = run_test_2(qm, stemmer)

    # --- Comparison ---
    print("=" * 90)
    print("COMPARISON SUMMARY")
    print("=" * 90)
    print(f"  {'Approach':<45} {'Unique Books':<15}")
    print(f"  {'-'*45} {'-'*15}")
    print(f"  {'Baseline (current, no filtering)':<45} {len(baseline_books):<15}")
    print(f"  {'Test 1 (all-word stemmed match on vector)':<45} {len(test1_books):<15}")
    print(f"  {'Test 2 (adaptive score threshold)':<45} {len(test2_books):<15}")
    print()


if __name__ == "__main__":
    main()
