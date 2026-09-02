import os

# ============================================================================
# Bookito Prompt Classifiers Constants
# ============================================================================
# This file centralizes all hardcoded strings, configurations, and paths.
# As per the rules, we avoid hardcoding values deep in the implementation
# and keep them here so they can be easily shared across all 7 models.
# ============================================================================

# ----------------------------------------------------------------------------
# File Paths & Directories
# ----------------------------------------------------------------------------
# Determine the absolute root of the repository. This assumes that this constants.py 
# file is located at `Bookito/classifiers/prompt/common/constants.py`, 
# so we go up 3 levels to get the root `Bookito/` directory.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Path to the directory where JSON dataset files are stored.
DATA_DIR = os.path.join(BASE_DIR, "data")

# Path to the categories definitions
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")

# Pattern for identifying the prompt training files
PROMPTS_FILE_PREFIX = "test_prompts_randomized_v2_"
PROMPTS_FILE_EXT = ".json"

# Directory name to save the trained models inside each approach's folder
MODEL_SAVE_DIR_NAME = "saved_model"

# ----------------------------------------------------------------------------
# Dataset & Model Constants
# ----------------------------------------------------------------------------
# The total number of categories we expect to classify the prompts into.
# Knowing this helps to configure the output layers of our ML models.
NUM_CLASSES = 54

# Random seed to ensure reproducibility across runs, especially for PyTorch 
# initialization and scikit-learn train_test_split.
RANDOM_SEED = 42

# Default test/validation split ratio
VAL_SPLIT_SIZE = 0.15
TEST_SPLIT_SIZE = 0.15

# ----------------------------------------------------------------------------
# Training Hyperparameters (Default values used by Neural Network models)
# ----------------------------------------------------------------------------
# The number of samples processed before the model's internal parameters are updated.
DEFAULT_BATCH_SIZE = 32

# Number of complete passes through the training dataset.
DEFAULT_EPOCHS = 10

# Learning rate determines the step size at each iteration while moving toward a minimum of a loss function.
DEFAULT_LEARNING_RATE = 1e-3

# The maximum sequence length used when tokenizing prompts (used by Transformers, CNNs, LSTMs).
# Prompts longer than this will be truncated; shorter prompts will be padded.
MAX_SEQ_LENGTH = 128
