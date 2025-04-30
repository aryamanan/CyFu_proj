import kagglehub
import pandas as pd
from typing import List, Dict
import os
import json

class RecipeNLGLoader:
    def __init__(self, cache_dir: str = "recipe_data"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.dataset_path = os.path.join(cache_dir, "RecipeNLG_dataset.csv")

    def download_dataset(self) -> str:
        """Download the RecipeNLG dataset if not already present."""
        if not os.path.exists(self.dataset_path):
            print("Downloading RecipeNLG dataset...")
            path = kagglehub.dataset_download("paultimothymooney/recipenlg")
            # Move the dataset to our cache directory
            os.rename(os.path.join(path, "RecipeNLG_dataset.csv"), self.dataset_path)
        return self.dataset_path

    def load_dataset(self) -> pd.DataFrame:
        """Load the RecipeNLG dataset into a pandas DataFrame."""
        dataset_path = self.download_dataset()
        return pd.read_csv(dataset_path)

    def process_recipe(self, row: pd.Series) -> Dict:
        """Process a single recipe row into our standard format."""
        # Convert ingredients string to list
        ingredients = json.loads(row['ingredients'])
        
        # Convert directions string to list
        directions = json.loads(row['directions'])
        
        # Extract NER tags if available
        ner_tags = []
        if 'NER' in row and pd.notna(row['NER']):
            try:
                ner_tags = json.loads(row['NER'])
            except:
                ner_tags = []

        return {
            'title': row['title'],
            'ingredients': ingredients,
            'instructions': directions,
            'source': row['source'],
            'link': row['link'],
            'ner_tags': ner_tags,
            'cooking_time': self._estimate_cooking_time(directions),
            'difficulty': self._estimate_difficulty(ingredients, directions)
        }

    def _estimate_cooking_time(self, directions: List[str]) -> str:
        """Estimate cooking time based on number of steps."""
        num_steps = len(directions)
        if num_steps <= 3:
            return "15-30 minutes"
        elif num_steps <= 6:
            return "30-45 minutes"
        elif num_steps <= 10:
            return "45-60 minutes"
        else:
            return "60+ minutes"

    def _estimate_difficulty(self, ingredients: List[str], directions: List[str]) -> str:
        """Estimate recipe difficulty based on ingredients and steps."""
        num_ingredients = len(ingredients)
        num_steps = len(directions)
        
        if num_ingredients <= 5 and num_steps <= 5:
            return "Easy"
        elif num_ingredients <= 10 and num_steps <= 10:
            return "Medium"
        else:
            return "Hard"

    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes from the dataset in our standard format."""
        df = self.load_dataset()
        return [self.process_recipe(row) for _, row in df.iterrows()]

    def get_recipes_by_ingredients(self, ingredients: List[str], limit: int = 100) -> List[Dict]:
        """Get recipes that contain any of the specified ingredients."""
        df = self.load_dataset()
        # Convert ingredients to lowercase for case-insensitive matching
        ingredients = [ing.lower() for ing in ingredients]
        
        # Filter recipes containing any of the specified ingredients
        matching_recipes = []
        for _, row in df.iterrows():
            recipe_ingredients = json.loads(row['ingredients'])
            recipe_ingredients = [ing.lower() for ing in recipe_ingredients]
            
            if any(ing in ' '.join(recipe_ingredients) for ing in ingredients):
                matching_recipes.append(self.process_recipe(row))
                if len(matching_recipes) >= limit:
                    break
        
        return matching_recipes 