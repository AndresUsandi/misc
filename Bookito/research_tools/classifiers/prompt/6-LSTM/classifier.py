import argparse
from model import ClassifierTextLSTM

# ============================================================================
# CLI Driver for LSTM Text Classifier
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="LSTM Text Prompt Classifier")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["Train", "Infer", "Infer-Test", "Infer-Test-All"], 
        required=True,
        help="Whether to train a new model or infer using an existing one."
    )
    parser.add_argument(
        "--prompt", 
        type=str, 
        help="The text prompt to classify. Required if --mode is Infer."
    )
    
    args = parser.parse_args()
    
    classifier = ClassifierTextLSTM()
    
    if args.mode == "Train":
        classifier.train()
    elif args.mode == "Infer":
        if not args.prompt:
            parser.error("--prompt is required when --mode is Infer")
            
        print(f"Classifying prompt:\n'{args.prompt}'\n")
        
        prediction = classifier.infer(args.prompt)
        
        print("-" * 40)
        print(f"Predicted Category: {prediction}")
        print("-" * 40)

    elif args.mode == "Infer-Test":
        from common.data_loader import get_random_test_sample
        prompt, true_category = get_random_test_sample()
        
        print(f"Random Test Prompt:\n'{prompt}'\n")
        prediction = classifier.infer(prompt)
        
        print("-" * 40)
        print(f"True Category:      {true_category}")
        print(f"Predicted Category: {prediction}")
        print("-" * 40)
        
        if prediction == true_category:
            print("\033[92mSUCCESS: MATCH\033[0m")
        else:
            print("\033[91m")
            print("*" * 40)
            print("FAILURE: CATEGORY MISMATCH!")
            print("*" * 40)
            print("\033[0m")
            
    elif args.mode == "Infer-Test-All":
        from common.data_loader import get_all_test_samples
        prompts, true_categories = get_all_test_samples()
        
        success_count = 0
        total_count = len(prompts)
        
        for idx in range(total_count):
            prompt = prompts[idx]
            true_category = true_categories[idx]
            
            print(f"\n[Test {idx+1}/{total_count}]")
            print(f"Prompt:\n'{prompt}'\n")
            
            prediction = classifier.infer(prompt)
            
            print(f"True Category:      {true_category}")
            print(f"Predicted Category: {prediction}")
            
            if prediction == true_category:
                print("\033[92mSUCCESS: MATCH\033[0m")
                success_count += 1
            else:
                print("\033[91mFAILURE: CATEGORY MISMATCH!\033[0m")
                
        print("\n" + "=" * 40)
        print("TEST SET RESULTS")
        print("=" * 40)
        print(f"Total Tests: {total_count}")
        print(f"Successful:  {success_count}")
        print(f"Failed:      {total_count - success_count}")
        print(f"Accuracy:    {(success_count / total_count) * 100:.2f}%")
        print("=" * 40)

if __name__ == "__main__":
    main()
