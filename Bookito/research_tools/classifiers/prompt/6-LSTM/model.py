import os
import sys
import time
import pickle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, accuracy_score

from common.data_loader import get_train_val_test_split, SimpleVocab, SequenceDataset, get_label_encoders
from common.constants import NUM_CLASSES, DEFAULT_BATCH_SIZE, DEFAULT_EPOCHS, DEFAULT_LEARNING_RATE, MODEL_SAVE_DIR_NAME

# ============================================================================
# PyTorch Architectures
# ============================================================================
class TextLSTM(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int, num_classes: int, num_layers: int = 2):
        super(TextLSTM, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim, padding_idx=0)
        
        self.lstm = nn.LSTM(
            input_size=embed_dim, 
            hidden_size=hidden_dim, 
            num_layers=num_layers, 
            batch_first=True, 
            bidirectional=True,
            dropout=0.5 if num_layers > 1 else 0
        )
        
        self.fc = nn.Linear(hidden_dim * 4, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        
        avg_pool = torch.mean(lstm_out, dim=1)
        max_pool, _ = torch.max(lstm_out, dim=1)
        
        cat = torch.cat((avg_pool, max_pool), dim=1)
        dropped = self.dropout(cat)
        
        return self.fc(dropped)

# ============================================================================
# Model 6: ClassifierTextLSTM
# ============================================================================
class ClassifierTextLSTM:
    """
    Object-Oriented wrapper for the LSTM Classifier.
    """
    def __init__(self):
        self.vocab_path = os.path.join(os.path.dirname(__file__), "vocab.bin")
        self.model_path = os.path.join(os.path.dirname(__file__), "model-weights.bin")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vocab = None
        self.model = None
        
        self.embed_dim = 128
        self.hidden_dim = 128
        self.num_layers = 2
        
        _, self.id_to_label = get_label_encoders()

    def train(self):
        print("=" * 60)
        print("Training ClassifierTextLSTM")
        print("=" * 60)
        
        X_train_text, X_val_text, _, y_train, y_val, _, id_to_label = get_train_val_test_split()
        
        print("Building vocabulary...")
        self.vocab = SimpleVocab(max_size=20000)
        self.vocab.build(X_train_text)
        
        X_train_ids = [self.vocab.encode(text) for text in X_train_text]
        X_val_ids = [self.vocab.encode(text) for text in X_val_text]
        
        train_dataset = SequenceDataset(X_train_ids, y_train)
        val_dataset = SequenceDataset(X_val_ids, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=DEFAULT_BATCH_SIZE, shuffle=False)
        
        self.model = TextLSTM(
            vocab_size=len(self.vocab.word2id), 
            embed_dim=self.embed_dim, 
            hidden_dim=self.hidden_dim,
            num_classes=NUM_CLASSES,
            num_layers=self.num_layers
        ).to(self.device)
        
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
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
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
        if self.vocab is None or self.model is None:
            return
            
        with open(self.vocab_path, 'wb') as f:
            pickle.dump(self.vocab, f)
        torch.save(self.model.state_dict(), self.model_path)
        print(f"Model saved to {os.path.dirname(__file__)}")

    def load(self):
        if not os.path.exists(self.vocab_path) or not os.path.exists(self.model_path):
            raise FileNotFoundError("Saved model files not found. Run training first.")
            
        with open(self.vocab_path, 'rb') as f:
            self.vocab = pickle.load(f)
            
        self.model = TextLSTM(
            vocab_size=len(self.vocab.word2id), 
            embed_dim=self.embed_dim, 
            hidden_dim=self.hidden_dim,
            num_classes=NUM_CLASSES,
            num_layers=self.num_layers
        ).to(self.device)
        
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.eval()
        
    def infer(self, prompt: str) -> str:
        if self.model is None:
            self.load()
            
        ids = self.vocab.encode(prompt)
        tensor_vec = torch.tensor([ids], dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor_vec)
            _, predicted = torch.max(outputs, 1)
            
        prediction_id = predicted.item()
        return self.id_to_label[prediction_id]
