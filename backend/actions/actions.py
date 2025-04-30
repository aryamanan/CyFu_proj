# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Import your RecipeKnowledgeBase
# Ensure the path is correct relative to the backend directory
# If knowledge_base is not a package, adjust the import
import sys
import os
# Add the project root to the Python path to allow imports from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from knowledge_base.recipe_db import RecipeKnowledgeBase

# Import spaCy
import spacy

# --- Initialize SpaCy Model ONCE ---
print("Loading spaCy model...")
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print(
        "Downloading spaCy model en_core_web_md. This may take a while..."
    )
    from spacy.cli import download
    download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")
print("spaCy model loaded.")
# ----------------------------------

# --- Initialize Knowledge Base ONCE when action server starts ---
print("Initializing Recipe Knowledge Base for Action Server...")
# This assumes recipe_db.py is correctly implemented to load the CSV
try:
    recipe_kb_instance = RecipeKnowledgeBase()
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize RecipeKnowledgeBase: {e}")
    # Decide how to handle this - maybe exit, or run with an empty KB
    recipe_kb_instance = None 
print("Knowledge Base Initialized.")
# ---------------------------------------------------------------

class ActionQueryRecipeKb(Action):

    def name(self) -> Text:
        return "action_query_recipe_kb"

    def _extract_dish_name(self, text: str) -> Optional[str]:
        """Extracts a likely dish name using spaCy (noun chunks)."""
        # Basic cleanup of common phrases
        text = text.lower()
        phrases_to_remove = [
            "i want a recipe for", "recipe for", "how to make", "how do i make",
            "find a recipe for", "get me the recipe for", "get me", 
            "what about", "instructions for", "show me how to prepare",
            "i need a", "recipe please", "recipe"
        ]
        for phrase in phrases_to_remove:
            text = text.replace(phrase, "")
        text = text.strip()

        if not text: # Return None if text is empty after cleanup
            return None

        # Use spaCy for noun chunks
        doc = nlp(text)
        
        # Try taking the last noun chunk as the most likely dish name
        if doc.noun_chunks:
            dish_name = list(doc.noun_chunks)[-1].text
            print(f"spaCy extracted dish name (noun chunk): {dish_name}")
            return dish_name.strip()
            
        # Fallback: if no noun chunks, return the cleaned text
        print(f"spaCy fallback - using cleaned text: {text}")
        return text.strip()

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Use the globally initialized knowledge base instance
        if not recipe_kb_instance or recipe_kb_instance.recipes_df.empty:
            print("Error: Knowledge base is not available or empty.")
            dispatcher.utter_message(text="Sorry, my recipe knowledge base isn't available right now.")
            return []

        # Get the full user message text
        user_message = tracker.latest_message.get('text')
        if not user_message:
             dispatcher.utter_message(text="I couldn't understand your message.")
             return []
             
        print(f"Received user message: {user_message}")

        # Extract dish name using spaCy
        dish_name = self._extract_dish_name(user_message)

        if not dish_name:
            # This might happen if the message was only stop words after cleaning
            dispatcher.utter_message(text="I couldn't figure out the dish name from your message. Could you try again?")
            return []

        # Search for the recipe using the spaCy-extracted name
        try:
            print(f"Action searching for dish (from spaCy): {dish_name}") # Add logging
            query = dish_name # Use the extracted name directly for search
            recipes = recipe_kb_instance.search_recipes(query, n_results=1)
            print(f"Found recipes: {bool(recipes)}") # Add logging

            if recipes:
                recipe = recipes[0] # Assuming search_recipes returns a list of dicts
                print(f"Recipe found: {recipe.get('title')}") # Add logging
                
                # --- Remove Temporary ---
                # test_response_text = f"Action found recipe: {recipe.get('title')}"
                # print(f"Dispatching TEST message: {test_response_text}")
                # dispatcher.utter_message(text=test_response_text)
                # --- End Remove ---

                # --- Restore Original formatting ---
                ingredients_text = "\n".join([f"- {ing}" for ing in recipe.get('ingredients', [])])
                instructions_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe.get('instructions', []))])
                
                response_text = (
                    f"Found a recipe for {recipe.get('title', dish_name)}!\n\n"
                    f"**Ingredients:**\n{ingredients_text}\n\n"
                    f"**Instructions:**\n{instructions_text}\n\n"
                    f"Cooking Time: {recipe.get('cooking_time', 'N/A')}\n"
                    f"Difficulty: {recipe.get('difficulty', 'N/A')}"
                )
                if recipe.get('link'):
                    response_text += f"\nLink: {recipe['link']}"
                                    
                dispatcher.utter_message(text=response_text)
                # --- End Restore ---
            else:
                print(f"No recipe found for: {dish_name}") # Add logging
                # Use the defined response from domain.yml
                dispatcher.utter_message(response="utter_recipe_not_found")

        except Exception as e:
            print(f"Error querying knowledge base in action: {e}") # Log the error
            dispatcher.utter_message(text="Sorry, I encountered an error while searching for the recipe.")

        return []

# Remove or comment out the default HelloWorld action if it exists
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
