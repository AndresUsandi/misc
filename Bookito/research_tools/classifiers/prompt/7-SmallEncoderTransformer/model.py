import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, accuracy_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from common.data_loader import get_train_val_test_split, get_label_encoders
from common.constants import NUM_CLASSES, DEFAULT_EPOCHS, MAX_SEQ_LENGTH, MODEL_SAVE_DIR_NAME

# ============================================================================
# PyTorch Architectures
# ============================================================================
class TransformerDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

# ============================================================================
# Model 7: ClassifierTransformer
# ============================================================================
class ClassifierTransformer:
    """
    Object-Oriented wrapper for the Small Encoder Transformer (DistilBERT).
    """
    def __init__(self):
        self.save_dir = os.path.dirname(__file__)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = "distilbert-base-uncased"
        self.learning_rate = 2e-5
        
        self.tokenizer = None
        self.model = None
        
        _, self.id_to_label = get_label_encoders()

    def train(self):
        print("=" * 60)
        print("Training ClassifierTransformer")
        print("=" * 60)
        
        X_train_text, X_val_text, _, y_train, y_val, _, id_to_label = get_train_val_test_split()
        
        print(f"\nLoading Tokenizer ({self.model_name})...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        print("Tokenizing training data...")
        train_encodings = self.tokenizer(X_train_text, truncation=True, padding=True, max_length=MAX_SEQ_LENGTH)
        
        print("Tokenizing validation data...")
        val_encodings = self.tokenizer(X_val_text, truncation=True, padding=True, max_length=MAX_SEQ_LENGTH)
        
        train_dataset = TransformerDataset(train_encodings, y_train)
        val_dataset = TransformerDataset(val_encodings, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        
        print(f"\nLoading Pre-trained Model ({self.model_name})...")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, 
            num_labels=NUM_CLASSES
        ).to(self.device)
        
        optimizer = optim.AdamW(self.model.parameters(), lr=self.learning_rate)
        
        print("\nStarting Fine-Tuning... (This will take a while!)")
        best_val_loss = float('inf')
        patience = 2
        patience_counter = 0
        
        transformer_epochs = min(4, DEFAULT_EPOCHS)
        
        for epoch in range(transformer_epochs):
            start_time = time.time()
            self.model.train()
            train_loss = 0.0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                train_loss += loss.item() * input_ids.size(0)
                
            train_loss /= len(train_loader.dataset)
            
            # Validation
            self.model.eval()
            val_loss = 0.0
            val_preds = []
            val_targets = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    labels = batch['labels'].to(self.device)
                    
                    outputs = self.model(input_ids, attention_mask=attention_mask, labels=labels)
                    val_loss += outputs.loss.item() * input_ids.size(0)
                    
                    _, predicted = torch.max(outputs.logits, 1)
                    val_preds.extend(predicted.cpu().numpy())
                    val_targets.extend(labels.cpu().numpy())
                    
            val_loss /= len(val_loader.dataset)
            val_acc = accuracy_score(val_targets, val_preds)
            
            epoch_time = time.time() - start_time
            print(f"Epoch {epoch+1}/{transformer_epochs} | Time: {epoch_time:.2f}s | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping triggered after {epoch+1} epochs.")
                    break
                    
        print("\nFine-Tuning Complete.")
        
    def save(self):
        if self.model is None or self.tokenizer is None:
            return
            
        os.makedirs(self.save_dir, exist_ok=True)
        # HuggingFace provides a built-in method to save the model and tokenizer
        self.model.save_pretrained(self.save_dir)
        self.tokenizer.save_pretrained(self.save_dir)
        print(f"Model and tokenizer saved to {self.save_dir}")

    def load(self):
        if not os.path.exists(self.save_dir):
            raise FileNotFoundError("Saved model directory not found. Run training first.")
            
        self.tokenizer = AutoTokenizer.from_pretrained(self.save_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.save_dir).to(self.device)
        self.model.eval()
        
    def infer(self, prompt: str) -> str:
        if self.model is None:
            self.load()
            
        encodings = self.tokenizer(
            [prompt], 
            truncation=True, 
            padding=True, 
            max_length=MAX_SEQ_LENGTH, 
            return_tensors="pt"
        )
        
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            _, predicted = torch.max(outputs.logits, 1)
            
        prediction_id = predicted.item()
        return self.id_to_label[prediction_id]
