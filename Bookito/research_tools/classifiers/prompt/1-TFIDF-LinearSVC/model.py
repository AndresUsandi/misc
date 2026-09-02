import os
import sys
import time
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

from common.data_loader import get_train_val_test_split, get_label_encoders
from common.constants import MODEL_SAVE_DIR_NAME

# ============================================================================
# Model 1: ClassifierLinearSVC
# ============================================================================
class ClassifierLinearSVC:
    """
    Object-Oriented wrapper for the TF-IDF + LinearSVC model.
    Provides methods to train, save, load, and perform inference on single prompts.
    """
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "pipeline.bin")
        self.pipeline = None
        
        # Load encoders for inference decoding
        _, self.id_to_label = get_label_encoders()

    def _build_pipeline(self) -> Pipeline:
        """Constructs the untraind scikit-learn pipeline."""
        vectorizer = TfidfVectorizer(max_features=50000, stop_words='english', ngram_range=(1, 2))
        classifier = LinearSVC(C=1.0, random_state=42, max_iter=1000)
        return Pipeline([('tfidf', vectorizer), ('clf', classifier)])

    def train(self):
        """
        Executes the training loop, evaluates the model, and saves it to disk.
        """
        print("=" * 60)
        print("Training ClassifierLinearSVC")
        print("=" * 60)
        
        print("Loading data...")
        start_time = time.time()
        X_train, X_val, _, y_train, y_val, _, id_to_label = get_train_val_test_split()
        print(f"Data loaded in {time.time() - start_time:.2f} seconds.")
        
        self.pipeline = self._build_pipeline()
        
        print("\nTraining pipeline...")
        start_time = time.time()
        self.pipeline.fit(X_train, y_train)
        print(f"Training completed in {time.time() - start_time:.2f} seconds.")
        
        print("\nEvaluating on validation set...")
        y_pred = self.pipeline.predict(X_val)
        
        acc = accuracy_score(y_val, y_pred)
        print(f"\nOverall Accuracy: {acc:.4f}")
        
        target_names = [id_to_label[i] for i in range(len(id_to_label))]
        print("\nDetailed Classification Report:")
        print(classification_report(y_val, y_pred, target_names=target_names))
        
        self.save()

    def save(self):
        """Saves the trained pipeline to disk."""
        if self.pipeline is None:
            raise ValueError("Cannot save an untrained model.")
            
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
        print(f"Model successfully saved to {self.model_path}")

    def load(self):
        """Loads the trained pipeline from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Saved model not found at {self.model_path}. Please run training first.")
            
        with open(self.model_path, 'rb') as f:
            self.pipeline = pickle.load(f)
        print(f"Model loaded successfully from {self.model_path}")

    def infer(self, prompt: str) -> str:
        """
        Predicts the category for a single text prompt.
        
        Args:
            prompt (str): The text to classify.
            
        Returns:
            str: The predicted category name.
        """
        if self.pipeline is None:
            self.load()
            
        # The pipeline expects an iterable of strings, so we wrap the prompt in a list
        prediction_id = self.pipeline.predict([prompt])[0]
        
        # Convert numerical ID back to human-readable string
        return self.id_to_label[prediction_id]
