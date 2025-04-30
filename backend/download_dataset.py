import kagglehub
import os

print("Downloading RecipeNLG dataset...")

# Define the desired download directory (e.g., a 'datasets' folder within backend)
download_dir = os.path.join(os.path.dirname(__file__), "datasets")
os.makedirs(download_dir, exist_ok=True)

# Download the dataset to the specified directory
path = kagglehub.dataset_download(
    "paultimothymooney/recipenlg",
    path=download_dir
)

print(f"Dataset downloaded to: {path}")

# You might need to configure Kaggle API credentials first.
# See: https://github.com/Kaggle/kagglehub?tab=readme-ov-file#authenticate 