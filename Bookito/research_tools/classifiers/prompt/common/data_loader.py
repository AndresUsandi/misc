import os
import json
import glob
from typing import List, Tuple, Dict
from sklearn.model_selection import train_test_split
from .constants import (
    DATA_DIR, 
    CATEGORIES_FILE, 
    PROMPTS_FILE_PREFIX, 
    PROMPTS_FILE_EXT,
    RANDOM_SEED,
    TEST_SPLIT_SIZE
)

# ============================================================================
# Data Loader and Label Encoding Utility
# ============================================================================
# This module is responsible for loading the raw JSON data and providing it
# in a clean, consistent format (X, y) that can be easily consumed by any of
# the 7 classifier models we are building.
# ============================================================================

def load_categories() -> List[str]:
    """
    Loads the official list of 54 categories from the categories.json file.
    
    Returns:
        List[str]: A list containing the string names of the categories.
    """
    # Safety check: ensure the categories file actually exists before we try to open it.
    if not os.path.exists(CATEGORIES_FILE):
        raise FileNotFoundError(f"Categories file not found at {CATEGORIES_FILE}")
        
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Extract just the "name" field from each category object in the JSON
    categories = [cat["name"] for cat in data.get("categories", [])]
    return categories

def create_label_encoder(categories: List[str]) -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Creates a mapping from string category names to integer IDs (and vice versa).
    Machine learning models require numerical targets, not strings.
    
    Args:
        categories (List[str]): List of category string names.
        
    Returns:
        Tuple[Dict[str, int], Dict[int, str]]: 
            - label_to_id: e.g., {"Software Feature": 0, "Backend/API": 1, ...}
            - id_to_label: e.g., {0: "Software Feature", 1: "Backend/API", ...}
    """
    # Enumerate gives us pairs of (index, value). We use this to build our dictionaries.
    label_to_id = {name: idx for idx, name in enumerate(categories)}
    id_to_label = {idx: name for idx, name in enumerate(categories)}
    
    return label_to_id, id_to_label

def load_all_prompts() -> Tuple[List[str], List[str]]:
    """
    Scans the data directory for all files matching the prompt pattern, reads
    them, and extracts the 'prompt' text and the 'primaryCategory' target.
    
    Returns:
        Tuple[List[str], List[str]]: 
            - X: List of prompt texts (the input features)
            - y: List of category strings (the labels)
    """
    # Construct a wildcard path to find all relevant JSON files.
    # Example: E:\...\Bookito\data\test_prompts_randomized_v2_*.json
    search_pattern = os.path.join(DATA_DIR, f"{PROMPTS_FILE_PREFIX}*{PROMPTS_FILE_EXT}")
    
    # glob.glob finds all file paths matching the wildcard pattern
    file_paths = glob.glob(search_pattern)
    
    if not file_paths:
        raise FileNotFoundError(f"No prompt files found matching {search_pattern}")
    
    X = []
    y = []
    
    # Iterate through each file we found
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # The JSON structure expects an array of prompts under the "prompts" key
            prompts = data.get("prompts", [])
            for p in prompts:
                prompt_text = p.get("prompt", "")
                category = p.get("primaryCategory", "")
                
                # Only add to our lists if both fields actually have content
                if prompt_text and category:
                    X.append(prompt_text)
                    y.append(category)
                    
    return X, y

def get_train_val_test_split() -> Tuple[List[str], List[str], List[str], List[int], List[int], List[int], Dict[int, str]]:
    """
    Loads all data, encodes labels, and splits into train, val, and test sets.
    
    Returns:
        X_train, X_val, X_test: Feature lists
        y_train, y_val, y_test: Label lists
        id_to_label: Mapping dictionary
    """
    categories = load_categories()
    label_to_id, id_to_label = create_label_encoder(categories)
    
    # Step 2: Load the raw data arrays
    X_raw, y_raw = load_all_prompts()
    
    # Step 3: Convert string labels to numerical target IDs (filtering out any non-canonical legacy categories)
    filtered_X = []
    filtered_y = []
    for prompt_text, label in zip(X_raw, y_raw):
        if label in label_to_id:
            filtered_X.append(prompt_text)
            filtered_y.append(label_to_id[label])
            
    X_raw = filtered_X
    y_encoded = filtered_y
    
    # Step 4: Split data into training, validation, and test sets.
    # First split: Test set
    X_temp, X_test, y_temp, y_test = train_test_split(
        X_raw, 
        y_encoded, 
        test_size=TEST_SPLIT_SIZE, 
        random_state=RANDOM_SEED,
        stratify=y_encoded
    )
    
    # Second split: Train and Validation sets
    from common.constants import VAL_SPLIT_SIZE
    val_ratio = VAL_SPLIT_SIZE / (1.0 - TEST_SPLIT_SIZE)
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, 
        y_temp, 
        test_size=val_ratio, 
        random_state=RANDOM_SEED,
        stratify=y_temp
    )
    
    return X_train, X_val, X_test, y_train, y_val, y_test, id_to_label

import random

def get_random_test_sample() -> tuple[str, str]:
    X_train, X_val, X_test, y_train, y_val, y_test, id_to_label = get_train_val_test_split()
    idx = random.randint(0, len(X_test) - 1)
    prompt = X_test[idx]
    true_category = id_to_label[y_test[idx]]
    return prompt, true_category

def get_all_test_samples() -> tuple[list[str], list[str]]:
    """
    Retrieves all prompts and their true category strings from the test set.
    """
    _, _, X_test, _, _, y_test, id_to_label = get_train_val_test_split()
    true_categories = [id_to_label[y] for y in y_test]
    return X_test, true_categories

def get_label_encoders() -> Tuple[Dict[str, int], Dict[int, str]]:
    """
    Quickly loads just the categories and returns the label encoders.
    Used for inference mode to avoid loading the entire dataset.
    """
    categories = load_categories()
    return create_label_encoder(categories)

import re
from collections import Counter
import torch
from torch.utils.data import Dataset

# ----------------------------------------------------------------------------
# Shared NLP Utilities for Deep Learning Models
# ----------------------------------------------------------------------------
class SimpleVocab:
    """
    A simple vocabulary class to map words to integer IDs.
    Used by CNN and LSTM models to encode text.
    """
    def __init__(self, max_size=20000):
        self.max_size = max_size
        self.word2id = {"<PAD>": 0, "<UNK>": 1}
        self.id2word = {0: "<PAD>", 1: "<UNK>"}
        
    def build(self, texts):
        counter = Counter()
        for text in texts:
            words = self.tokenize(text)
            counter.update(words)
            
        common_words = counter.most_common(self.max_size - 2)
        for idx, (word, _) in enumerate(common_words, start=2):
            self.word2id[word] = idx
            self.id2word[idx] = word
            
    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())
        
    def encode(self, text, max_len=128):
        words = self.tokenize(text)
        ids = [self.word2id.get(w, 1) for w in words]
        
        if len(ids) > max_len:
            ids = ids[:max_len]
        elif len(ids) < max_len:
            ids = ids + [0] * (max_len - len(ids))
            
        return ids

class SequenceDataset(Dataset):
    """
    A generic PyTorch Dataset that holds sequences of integer word IDs.
    Used by CNN and LSTM models.
    """
    def __init__(self, X_ids, y_labels):
        self.X_ids = X_ids
        self.y_labels = y_labels

    def __len__(self):
        return len(self.X_ids)

    def __getitem__(self, idx):
        return torch.tensor(self.X_ids[idx], dtype=torch.long), torch.tensor(self.y_labels[idx], dtype=torch.long)
