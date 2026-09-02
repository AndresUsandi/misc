import os
import sys
import argparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROMPT_CLASSIFIERS_DIR = os.path.join(ROOT_DIR, "classifiers", "prompt")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if PROMPT_CLASSIFIERS_DIR not in sys.path:
    sys.path.insert(0, PROMPT_CLASSIFIERS_DIR)

try:
    from model import ClassifierWord2VecMLP
except ImportError:
    from web.model import ClassifierWord2VecMLP

# Top-of-File Constants
MODE_TRAIN = "Train"
MODE_INFER = "Infer"
MODE_INFER_TEST = "Infer-Test"
MODE_INFER_TEST_ALL = "Infer-Test-All"
SUPPORTED_MODES = [MODE_TRAIN, MODE_INFER, MODE_INFER_TEST, MODE_INFER_TEST_ALL]

FLAG_MODE = "--mode"
FLAG_PROMPT = "--prompt"

ARG_HELP_DESCRIPTION = "Word2Vec + MLP Prompt Classifier"
ARG_HELP_MODE = "Whether to train a new model or infer using an existing one."
ARG_HELP_PROMPT = "The text prompt to classify. Required if --mode is Infer."
ERROR_PROMPT_REQUIRED = "--prompt is required when --mode is Infer"

LOG_DIVIDER_DASH = "-" * 40
LOG_DIVIDER_STAR = "*" * 40
LOG_DIVIDER_EQUAL = "=" * 40

ANSI_GREEN_SUCCESS = "\033[92mSUCCESS: MATCH\033[0m"
ANSI_RED_FAILURE_ALL = "\033[91mFAILURE: CATEGORY MISMATCH!\033[0m"
ANSI_RED_START = "\033[91m"
ANSI_COLOR_END = "\033[0m"

LOG_CLASSIFYING_PROMPT_FORMAT = "Classifying prompt:\n'{prompt}'\n"
LOG_PREDICTED_CATEGORY_FORMAT = "Predicted Category: {prediction}"
LOG_TRUE_CATEGORY_FORMAT = "True Category:      {category}"
LOG_RANDOM_TEST_FORMAT = "Random Test Prompt:\n'{prompt}'\n"
LOG_TEST_INDEX_FORMAT = "\n[Test {index}/{total}]"
LOG_TEST_RESULTS_HEADER = "\n========================================\nTEST SET RESULTS\n========================================"
LOG_TOTAL_TESTS_FORMAT = "Total Tests: {total}"
LOG_SUCCESSFUL_FORMAT = "Successful:  {success}"
LOG_FAILED_FORMAT = "Failed:      {failed}"
LOG_ACCURACY_FORMAT = "Accuracy:    {accuracy:.2f}%"

# ============================================================================
# CLI Driver for Word2Vec + MLP
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description=ARG_HELP_DESCRIPTION)
    parser.add_argument(
        FLAG_MODE, 
        type=str, 
        choices=SUPPORTED_MODES, 
        required=True,
        help=ARG_HELP_MODE
    )
    parser.add_argument(
        FLAG_PROMPT, 
        type=str, 
        help=ARG_HELP_PROMPT
    )
    
    args = parser.parse_args()
    classifier = ClassifierWord2VecMLP()
    
    if args.mode == MODE_TRAIN:
        classifier.train()
    elif args.mode == MODE_INFER:
        if not args.prompt:
            parser.error(ERROR_PROMPT_REQUIRED)
            
        print(LOG_CLASSIFYING_PROMPT_FORMAT.format(prompt=args.prompt))
        prediction = classifier.infer(args.prompt)
        
        print(LOG_DIVIDER_DASH)
        print(LOG_PREDICTED_CATEGORY_FORMAT.format(prediction=prediction))
        print(LOG_DIVIDER_DASH)

    elif args.mode == MODE_INFER_TEST:
        from classifiers.prompt.common.data_loader import get_random_test_sample
        prompt, true_category = get_random_test_sample()
        
        print(LOG_RANDOM_TEST_FORMAT.format(prompt=prompt))
        prediction = classifier.infer(prompt)
        
        print(LOG_DIVIDER_DASH)
        print(LOG_TRUE_CATEGORY_FORMAT.format(category=true_category))
        print(LOG_PREDICTED_CATEGORY_FORMAT.format(prediction=prediction))
        print(LOG_DIVIDER_DASH)
        
        if prediction == true_category:
            print(ANSI_GREEN_SUCCESS)
        else:
            print(ANSI_RED_START)
            print(LOG_DIVIDER_STAR)
            print("FAILURE: CATEGORY MISMATCH!")
            print(LOG_DIVIDER_STAR)
            print(ANSI_COLOR_END)
            
    elif args.mode == MODE_INFER_TEST_ALL:
        from classifiers.prompt.common.data_loader import get_all_test_samples
        prompts, true_categories = get_all_test_samples()
        
        success_count = 0
        total_count = len(prompts)
        
        for idx in range(total_count):
            prompt = prompts[idx]
            true_category = true_categories[idx]
            
            print(LOG_TEST_INDEX_FORMAT.format(index=idx+1, total=total_count))
            print(LOG_CLASSIFYING_PROMPT_FORMAT.format(prompt=prompt))
            
            prediction = classifier.infer(prompt)
            
            print(LOG_TRUE_CATEGORY_FORMAT.format(category=true_category))
            print(LOG_PREDICTED_CATEGORY_FORMAT.format(prediction=prediction))
            
            if prediction == true_category:
                print(ANSI_GREEN_SUCCESS)
                success_count += 1
            else:
                print(ANSI_RED_FAILURE_ALL)
                
        print(LOG_TEST_RESULTS_HEADER)
        print(LOG_DIVIDER_EQUAL)
        print(LOG_TOTAL_TESTS_FORMAT.format(total=total_count))
        print(LOG_SUCCESSFUL_FORMAT.format(success=success_count))
        print(LOG_FAILED_FORMAT.format(failed=total_count - success_count))
        print(LOG_ACCURACY_FORMAT.format(accuracy=(success_count / total_count) * 100))
        print(LOG_DIVIDER_EQUAL)

if __name__ == "__main__":
    main()
