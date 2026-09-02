import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score
import gensim.downloader as api

# Ensure workspace root and classifier paths are available
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROMPT_CLASSIFIERS_DIR = os.path.join(ROOT_DIR, "classifiers", "prompt")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if PROMPT_CLASSIFIERS_DIR not in sys.path:
    sys.path.insert(0, PROMPT_CLASSIFIERS_DIR)

from classifiers.prompt.common.data_loader import get_train_val_test_split, get_label_encoders
from classifiers.prompt.common.constants import (
    NUM_CLASSES,
    DEFAULT_BATCH_SIZE,
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE
)

# Top-of-File Constants
MODEL_WEIGHTS_FILE_NAME = "model-weights.bin"
W2V_MODEL_NAME = "word2vec-google-news-300"
DEFAULT_EMBEDDING_DIM = 300
DEFAULT_HIDDEN_DIM = 256
DROPOUT_RATE = 0.2
EARLY_STOPPING_PATIENCE = 3
INITIAL_BEST_VAL_LOSS = float('inf')

CUDA_DEVICE_NAME = "cuda"
CPU_DEVICE_NAME = "cpu"

LOG_LOADING_W2V = "Loading Pretrained Word2Vec (Google News 300). This may take a while..."
LOG_MODEL_NOT_FOUND = "Saved model weights not found at {path}. Run training first."
LOG_TRAINING_HEADER = "============================================================\nTraining ClassifierWord2VecMLP\n============================================================"
LOG_CONVERTING_TRAIN_PROMPTS = "Converting training prompts to Word2Vec averages..."
LOG_CONVERTING_VAL_PROMPTS = "Converting validation prompts to Word2Vec averages..."
LOG_STARTING_TRAINING = "\nStarting Training..."
LOG_TRAINING_COMPLETE = "\nTraining Complete."
LOG_MODEL_SAVED_FORMAT = "Model saved to {dir}"
LOG_EARLY_STOPPING_FORMAT = "Early stopping triggered after {epoch} epochs."
LOG_EPOCH_METRICS_FORMAT = "Epoch {epoch}/{total_epochs} | Time: {time:.2f}s | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"

# ============================================================================
# PyTorch Architectures & Utils
# ============================================================================

def get_prompt_vector(text: str, w2v_model) -> np.ndarray:
    words = text.lower().split()
    vectors = []
    for word in words:
        if word in w2v_model:
            vectors.append(w2v_model[word])
            
    if len(vectors) == 0:
        return np.zeros(w2v_model.vector_size, dtype=np.float32)
        
    avg_vector = np.mean(vectors, axis=0)
    return avg_vector.astype(np.float32)

class DenseVectorDataset(Dataset):
    def __init__(self, X_vectors, y_labels):
        self.X_vectors = X_vectors
        self.y_labels = y_labels

    def __len__(self):
        return len(self.X_vectors)

    def __getitem__(self, idx):
        x_tensor = torch.tensor(self.X_vectors[idx], dtype=torch.float32)
        y_tensor = torch.tensor(self.y_labels[idx], dtype=torch.long)
        return x_tensor, y_tensor

class DenseMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int):
        super(DenseMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(DROPOUT_RATE),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, x):
        return self.network(x)

# ============================================================================
# ClassifierWord2VecMLP
# ============================================================================
class ClassifierWord2VecMLP:
    """
    Object-Oriented wrapper for the Word2Vec + MLP model.
    Provides methods to train, save, load, and perform inference.
    """
    def __init__(self):
        self.model_path = os.path.join(CURRENT_DIR, MODEL_WEIGHTS_FILE_NAME)
        self.device = torch.device(CUDA_DEVICE_NAME if torch.cuda.is_available() else CPU_DEVICE_NAME)
        self.w2v_model = None
        self.model = None
        
        self.embedding_dim = DEFAULT_EMBEDDING_DIM
        self.hidden_dim = DEFAULT_HIDDEN_DIM
        
        _, self.id_to_label = get_label_encoders()

    def _load_w2v(self):
        if self.w2v_model is None:
            print(LOG_LOADING_W2V)
            self.w2v_model = api.load(W2V_MODEL_NAME)
            self.embedding_dim = self.w2v_model.vector_size

    def train(self):
        print(LOG_TRAINING_HEADER)
        
        self._load_w2v()
        
        X_train_text, X_val_text, _, y_train, y_val, _, _ = get_train_val_test_split()
        
        print(LOG_CONVERTING_TRAIN_PROMPTS)
        X_train_vec = [get_prompt_vector(text, self.w2v_model) for text in X_train_text]
        print(LOG_CONVERTING_VAL_PROMPTS)
        X_val_vec = [get_prompt_vector(text, self.w2v_model) for text in X_val_text]
        
        train_dataset = DenseVectorDataset(X_train_vec, y_train)
        val_dataset = DenseVectorDataset(X_val_vec, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=False)
        
        self.model = DenseMLP(self.embedding_dim, self.hidden_dim, NUM_CLASSES).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=DEFAULT_LEARNING_RATE)
        
        print(LOG_STARTING_TRAINING)
        best_val_loss = INITIAL_BEST_VAL_LOSS
        patience = EARLY_STOPPING_PATIENCE
        patience_counter = 0
        
        for epoch in range(DEFAULT_EPOCHS):
            start_time = time.time()
            self.model.train()
            train_loss = 0.0
            
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                train_loss += loss.item() * batch_x.size(0)
                
            train_loss /= len(train_loader.dataset)
            
            # Validation
            self.model.eval()
            val_loss = 0.0
            val_preds = []
            val_targets = []
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_x)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item() * batch_x.size(0)
                    
                    _, predicted = torch.max(outputs, 1)
                    val_preds.extend(predicted.cpu().numpy())
                    val_targets.extend(batch_y.cpu().numpy())
                    
            val_loss /= len(val_loader.dataset)
            val_acc = accuracy_score(val_targets, val_preds)
            
            epoch_time = time.time() - start_time
            print(LOG_EPOCH_METRICS_FORMAT.format(
                epoch=epoch+1,
                total_epochs=DEFAULT_EPOCHS,
                time=epoch_time,
                train_loss=train_loss,
                val_loss=val_loss,
                val_acc=val_acc
            ))
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(LOG_EARLY_STOPPING_FORMAT.format(epoch=epoch+1))
                    break
                    
        print(LOG_TRAINING_COMPLETE)
        
    def save(self):
        if self.model is None:
            return
            
        torch.save(self.model.state_dict(), self.model_path)
        print(LOG_MODEL_SAVED_FORMAT.format(dir=CURRENT_DIR))

    def load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(LOG_MODEL_NOT_FOUND.format(path=self.model_path))
            
        self._load_w2v()
        self.model = DenseMLP(self.embedding_dim, self.hidden_dim, NUM_CLASSES).to(self.device)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.eval()
        
    def infer(self, prompt: str) -> str:
        if self.model is None:
            self.load()
            
        dense_vec = get_prompt_vector(prompt, self.w2v_model)
        tensor_vec = torch.tensor(dense_vec).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor_vec)
            _, predicted = torch.max(outputs, 1)
            
        prediction_id = predicted.item()
        return self.id_to_label[prediction_id]
