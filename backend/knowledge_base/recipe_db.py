import pandas as pd
import os
from typing import List, Dict, Optional
import ast # To safely evaluate string representations of lists

class RecipeKnowledgeBase:
    def __init__(self, csv_path="datasets/RecipeNLG_dataset.csv"):
        """Loads the recipe dataset from the specified CSV file."""
        script_dir = os.path.dirname(__file__)
        # Go up one level to the 'backend' directory for relative path
        base_dir = os.path.dirname(script_dir) 
        full_path = os.path.join(base_dir, csv_path)
        
        print(f"Loading dataset from: {full_path}")
        try:
            # Load only necessary columns and potentially sample for faster loading
            self.recipes_df = pd.read_csv(
                full_path,
                usecols=['title', 'ingredients', 'directions', 'link', 'source', 'NER'],
                # nrows=10000 # Uncomment to load only a subset for faster testing
            )
            self.recipes_df.dropna(subset=['title', 'ingredients', 'directions'], inplace=True)
            # Convert stringified lists in 'ingredients' and 'directions' back to actual lists
            # NER column seems to already be stringified lists in the dataset description
            print("Converting ingredients column...")
            self.recipes_df['ingredients'] = self.recipes_df['ingredients'].apply(self._safe_eval_list)
            print("Converting directions column...")
            self.recipes_df['directions'] = self.recipes_df['directions'].apply(self._safe_eval_list)
            print("Dataset loaded and processed.")
        except FileNotFoundError:
            print(f"Error: Dataset file not found at {full_path}")
            self.recipes_df = pd.DataFrame() # Initialize empty dataframe
        except Exception as e:
            print(f"Error loading or processing dataset: {e}")
            self.recipes_df = pd.DataFrame()
            
    def _safe_eval_list(self, list_str):
        """Safely evaluate a string representation of a list."""
        try:
            # Using ast.literal_eval is safer than eval()
            evaluated = ast.literal_eval(list_str)
            if isinstance(evaluated, list):
                return evaluated
            return [] # Return empty list if it's not a list
        except (ValueError, SyntaxError, TypeError):
            # Handle cases where the string is not a valid list representation
            return [] # Return empty list on error

    def search_recipes(self, query: str, n_results: int = 1) -> List[Dict]:
        """Performs a case-insensitive search on recipe titles, prioritizing exact matches."""
        if self.recipes_df.empty:
            return []
            
        # Basic query cleaning
        query_lower = query.lower().strip()
        
        # 1. Try exact (case-insensitive) title match first
        exact_match_results = self.recipes_df[
            self.recipes_df['title'].str.lower() == query_lower
        ]
        
        results_df = exact_match_results
        
        # 2. If no exact match, try case-insensitive substring contains
        if results_df.empty:
            # Avoid searching for generic terms if query is short after cleaning
            if len(query_lower) > 2: 
                substring_match_results = self.recipes_df[
                    self.recipes_df['title'].str.lower().str.contains(query_lower, na=False)
                ]
                results_df = substring_match_results
            else:
                 results_df = pd.DataFrame() # Empty dataframe if query is too short for substring
        
        if results_df.empty:
            return []
        
        # Convert found recipes to dictionary format
        output_recipes = []
        for _, row in results_df.head(n_results).iterrows():
            output_recipes.append({
                'title': row.get('title', 'N/A'),
                'ingredients': row.get('ingredients', []), 
                'instructions': row.get('directions', []), # Use 'directions' column
                'cooking_time': 'N/A',  # Placeholder - dataset doesn't have this directly
                'difficulty': 'N/A',    # Placeholder
                'link': row.get('link', None),
                'source': row.get('source', None),
                'ner': row.get('NER', []) # Include NER if needed later
            })
            
        return output_recipes

    def get_recipes_by_ingredients(self, ingredients: List[str], limit: int = 1) -> List[Dict]:
        """Placeholder for ingredient-based search."""
        # TODO: Implement actual ingredient-based search
        print(f"Ingredient search called with: {ingredients} (Not implemented)")
        # For now, just return empty or a dummy result
        return []

    def add_recipe(self, recipe: Dict):
        """Adds a single recipe to the DataFrame (in-memory only)."""
        if not self.recipes_df.empty:
            new_recipe_df = pd.DataFrame([recipe])
            self.recipes_df = pd.concat([self.recipes_df, new_recipe_df], ignore_index=True)
        else:
            self.recipes_df = pd.DataFrame([recipe])
        print(f"Recipe '{recipe.get('title')}' added to in-memory KB.") 