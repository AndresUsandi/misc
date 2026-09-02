import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, accuracy_score
from sentence_transformers import SentenceTransformer

from common.data_loader import get_train_val_test_split, get_label_encoders
from common.constants import NUM_CLASSES, DEFAULT_BATCH_SIZE, DEFAULT_EPOCHS, DEFAULT_LEARNING_RATE, MODEL_SAVE_DIR_NAME

# ============================================================================
# PyTorch Architectures
# ============================================================================
class SentenceEmbedDataset(Dataset):
    def __init__(self, X_vectors, y_labels):
        self.X_vectors = X_vectors
        self.y_labels = y_labels

    def __len__(self):
        return len(self.X_vectors)

    def __getitem__(self, idx):
        y_tensor = torch.tensor(self.y_labels[idx], dtype=torch.long)
        return self.X_vectors[idx], y_tensor

class SentenceMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_classes: int):
        super(SentenceMLP, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes)
        )

    def forward(self, x):
        return self.network(x)

# ============================================================================
# Model 4: ClassifierSentenceEmbeddings
# ============================================================================
class ClassifierSentenceEmbeddings:
    """
    Object-Oriented wrapper for the Sentence Embeddings + MLP model.
    """
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "model-weights.bin")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedder = None
        self.model = None
        
        # 'all-MiniLM-L6-v2' output dimension is 384
        self.embedding_dim = 384 
        self.hidden_dim = 256
        
        _, self.id_to_label = get_label_encoders()

    def _load_embedder(self):
        if self.embedder is None:
            print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            self.embedding_dim = self.embedder.get_sentence_embedding_dimension()

    def train(self):
        print("=" * 60)
        print("Training ClassifierSentenceEmbeddings")
        print("=" * 60)
        
        self._load_embedder()
        
        X_train_text, X_val_text, _, y_train, y_val, _, id_to_label = get_train_val_test_split()
        
        print("Encoding training data... (This might take a few minutes)")
        start_time = time.time()
        X_train_vec = self.embedder.encode(X_train_text, convert_to_tensor=True, show_progress_bar=True)
        print(f"Train encoding finished in {time.time() - start_time:.2f} seconds.")
        
        print("Encoding validation data...")
        X_val_vec = self.embedder.encode(X_val_text, convert_to_tensor=True, show_progress_bar=True)
        
        X_train_vec = X_train_vec.cpu()
        X_val_vec = X_val_vec.cpu()
        
        train_dataset = SentenceEmbedDataset(X_train_vec, y_train)
        val_dataset = SentenceEmbedDataset(X_val_vec, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=False)
        
        self.model = SentenceMLP(self.embedding_dim, self.hidden_dim, NUM_CLASSES).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=DEFAULT_LEARNING_RATE)
        
        print("\nStarting Training...")
        best_val_loss = float('inf')
        patience = 3
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
            print(f"Epoch {epoch+1}/{DEFAULT_EPOCHS} | Time: {epoch_time:.2f}s | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping triggered after {epoch+1} epochs.")
                    break
                    
        print("\nTraining Complete.")
        
    def save(self):
        if self.model is None:
            return
            
        torch.save(self.model.state_dict(), self.model_path)
        print(f"Model saved to {os.path.dirname(__file__)}")

    def load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError("Saved model files not found. Run training first.")
            
        self._load_embedder()
        self.model = SentenceMLP(self.embedding_dim, self.hidden_dim, NUM_CLASSES).to(self.device)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.eval()
        
    def infer(self, prompt: str) -> str:
        if self.model is None:
            self.load()
            
        # Encode the single prompt to a tensor
        tensor_vec = self.embedder.encode([prompt], convert_to_tensor=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor_vec)
            _, predicted = torch.max(outputs, 1)
            
        prediction_id = predicted.item()
        return self.id_to_label[prediction_id]
