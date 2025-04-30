# AI Recipe Chatbot (Rasa + React)

This project implements a conversational AI recipe chatbot using Rasa for the backend NLU and dialogue management, and React for the frontend user interface.

## Project Structure

- `backend/`: Contains the Rasa project, custom actions, and knowledge base logic.
- `frontend/`: Contains the React frontend application.

## Setup

**Prerequisites:**

- Python 3.10
- Node.js and npm (or yarn)
- Kaggle Account & API Credentials (`kaggle.json` - see [Kaggle API Docs](https://www.kaggle.com/docs/api))

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aryamanan/CyFu_proj.git
    cd CyFu_proj
    ```

2.  **Setup Backend Virtual Environment:**
    ```bash
    cd backend
    python3.10 -m venv venv
    source venv/bin/activate 
    ```
    *(Use `venv\Scripts\activate` on Windows)*

3.  **Install Backend Dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  **Download Recipe Dataset:**
    *   Ensure your `kaggle.json` is set up correctly (usually in `~/.kaggle/kaggle.json`).
    *   Download the dataset zip using the provided script or curl:
        ```bash
        # Option 1: Using script (might require kagglehub install)
        # pip install kagglehub
        # python download_dataset.py 
        
        # Option 2: Using curl
        curl -L -o ~/Downloads/recipenlg.zip https://www.kaggle.com/api/v1/datasets/download/paultimothymooney/recipenlg
        ```
    *   Unzip and place the CSV:
        ```bash
        unzip ~/Downloads/recipenlg.zip -d ~/Downloads/recipenlg_extracted
        mkdir -p datasets 
        mv ~/Downloads/recipenlg_extracted/RecipeNLG_dataset.csv datasets/
        # Clean up (optional)
        # rm ~/Downloads/recipenlg.zip
        # rm -rf ~/Downloads/recipenlg_extracted
        ```
    *(Adjust paths as needed based on where you downloaded/extracted)*

5.  **Train Rasa Model:**
    *(Still in `backend/` with venv active)*
    ```bash
    rasa train
    ```

6.  **Setup Frontend:**
    ```bash
    cd ../frontend 
    npm install 
    ```
    *(Or `yarn install` if you use yarn)*

## Running the Application

**Important:** The backend requires two separate terminal sessions.

1.  **Terminal 1: Start Rasa Action Server:**
    ```bash
    cd backend
    source venv/bin/activate
    rasa run actions
    ```
    *Wait for it to load the spaCy model and dataset, and print `Action endpoint is up and running...`*

2.  **Terminal 2: Start Rasa Core Server:**
    ```bash
    cd backend
    source venv/bin/activate
    rasa run --enable-api --cors "*"
    ```
    *Wait for it to load the model and print `Rasa server is up and running.`*

3.  **Terminal 3: Start Frontend Development Server:**
    ```bash
    cd frontend
    npm start
    ```
    *(Or `yarn start`)*

4.  Open your browser to `http://localhost:3000` (or the address provided by `npm start`). You should now be able to chat with the recipe bot! 