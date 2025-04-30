from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from knowledge_base.recipe_db import RecipeKnowledgeBase
import json

class ActionGenerateRecipe(Action):
    def name(self) -> Text:
        return "action_generate_recipe"

    def __init__(self):
        self.kb = RecipeKnowledgeBase()

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        # Get slots from conversation
        dish_name = tracker.get_slot("dish_name")
        cuisine_type = tracker.get_slot("cuisine_type")
        ingredients = tracker.get_slot("ingredients")
        dietary_restrictions = tracker.get_slot("dietary_restrictions")
        cooking_preferences = tracker.get_slot("cooking_preferences")

        # Create search query
        query = f"{dish_name} {cuisine_type} recipe"
        if ingredients:
            query += f" with {', '.join(ingredients)}"
        if dietary_restrictions:
            query += f" {', '.join(dietary_restrictions)}"
        if cooking_preferences:
            query += f" {cooking_preferences}"

        # Search for matching recipes
        recipes = self.kb.search_recipes(query, n_results=1)
        
        if recipes:
            recipe = recipes[0]
            # Format recipe details
            recipe_details = f"""
            Title: {recipe['title']}
            Cuisine: {recipe['cuisine']}
            Cooking Time: {recipe['cooking_time']}
            Difficulty: {recipe['difficulty']}
            
            Ingredients:
            {chr(10).join(f'- {ing}' for ing in recipe['ingredients'])}
            
            Instructions:
            {chr(10).join(f'{i+1}. {step}' for i, step in enumerate(recipe['instructions']))}
            """
            
            # Set recipe details in slot
            return [SlotSet("recipe_details", recipe_details)]
        else:
            dispatcher.utter_message(text="I couldn't find a matching recipe. Would you like to try a different dish?")
            return []

class ActionUploadRecipe(Action):
    def name(self) -> Text:
        return "action_upload_recipe"

    def __init__(self):
        self.kb = RecipeKnowledgeBase()
        self.extractor = PDFRecipeExtractor()

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        # Get the uploaded file path from the tracker
        file_path = tracker.get_slot("file_path")
        
        if not file_path:
            dispatcher.utter_message(text="No file was uploaded. Please try again.")
            return []

        try:
            # Extract recipes from PDF
            recipes = self.extractor.process_pdf(file_path)
            
            # Add recipes to knowledge base
            for recipe in recipes:
                self.kb.add_recipe(recipe)
            
            dispatcher.utter_message(text=f"Successfully added {len(recipes)} recipes to the knowledge base.")
            return []
            
        except Exception as e:
            dispatcher.utter_message(text=f"Error processing the file: {str(e)}")
            return [] 