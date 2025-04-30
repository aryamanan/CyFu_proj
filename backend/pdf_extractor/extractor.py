from PyPDF2 import PdfReader
import re
from typing import List, Dict
import json

class PDFRecipeExtractor:
    def __init__(self):
        self.recipe_patterns = {
            'title': r'^(.*?)(?=\nIngredients:)',
            'ingredients': r'Ingredients:(.*?)(?=\nInstructions:)',
            'instructions': r'Instructions:(.*?)(?=\nCooking Time:|$)',
            'cooking_time': r'Cooking Time: (.*?)(?=\n|$)',
            'difficulty': r'Difficulty: (.*?)(?=\n|$)',
            'cuisine': r'Cuisine: (.*?)(?=\n|$)'
        }

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def parse_recipe(self, text: str) -> Dict:
        """Parse recipe text into structured format."""
        recipe = {}
        for key, pattern in self.recipe_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                value = match.group(1).strip()
                if key == 'ingredients':
                    recipe[key] = [ing.strip() for ing in value.split('\n') if ing.strip()]
                elif key == 'instructions':
                    recipe[key] = [step.strip() for step in value.split('\n') if step.strip()]
                else:
                    recipe[key] = value
        return recipe

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """Process PDF file and extract all recipes."""
        text = self.extract_text(pdf_path)
        # Split text into individual recipes (assuming each recipe starts with a title)
        recipe_texts = re.split(r'\n(?=[A-Z])', text)
        recipes = []
        for recipe_text in recipe_texts:
            if any(keyword in recipe_text.lower() for keyword in ['ingredients', 'instructions']):
                recipe = self.parse_recipe(recipe_text)
                if recipe:
                    recipes.append(recipe)
        return recipes 