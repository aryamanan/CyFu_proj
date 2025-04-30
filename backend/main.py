from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from pdf_extractor.extractor import PDFRecipeExtractor
from knowledge_base.recipe_db import RecipeKnowledgeBase
import tempfile

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
recipe_kb = RecipeKnowledgeBase()
pdf_extractor = PDFRecipeExtractor()

class RecipeRequest(BaseModel):
    dish_name: str
    cuisine_type: Optional[str] = None
    ingredients: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    cooking_preferences: Optional[str] = None

class RecipeResponse(BaseModel):
    title: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: str
    difficulty: str
    source: Optional[str] = None
    link: Optional[str] = None

@app.post("/upload-recipes")
async def upload_recipes(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Extract recipes from PDF
        recipes = pdf_extractor.process_pdf(temp_path)
        
        # Add recipes to knowledge base
        for recipe in recipes:
            recipe_kb.add_recipe(recipe)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {"message": f"Successfully added {len(recipes)} recipes to the knowledge base"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    try:
        # Create search query
        query = f"{request.dish_name} recipe"
        if request.cuisine_type:
            query += f" {request.cuisine_type}"
        if request.ingredients:
            query += f" with {', '.join(request.ingredients)}"
        if request.dietary_restrictions:
            query += f" {', '.join(request.dietary_restrictions)}"
        if request.cooking_preferences:
            query += f" {request.cooking_preferences}"

        # Search for matching recipes
        recipes = recipe_kb.search_recipes(query, n_results=1)
        
        if not recipes:
            # If no results found, try searching by ingredients
            if request.ingredients:
                recipes = recipe_kb.get_recipes_by_ingredients(request.ingredients, limit=1)
            
            if not recipes:
                raise HTTPException(status_code=404, detail="No matching recipe found")
        
        recipe = recipes[0]
        return RecipeResponse(
            title=recipe['title'],
            ingredients=recipe['ingredients'],
            instructions=recipe['instructions'],
            cooking_time=recipe['cooking_time'],
            difficulty=recipe['difficulty'],
            source=recipe.get('source'),
            link=recipe.get('link')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Recipe Generator API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 