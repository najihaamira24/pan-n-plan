# Pan n Plan

A recipe book web application built with Flask and SQLite. Users can browse and search recipes and save favorites, while creators can publish and manage their own recipes with photos.

## Features
- Register and log in as a **Creator** or a **Regular User**
- Creator dashboard: create and delete recipes, with image upload
- Search recipes and view recipe details (ingredients, instructions, category, cooking time, servings)
- Save and remove favorite recipes
- Upload a profile image

## Tech Stack
- Python, Flask, Jinja2 templates
- SQLite
- Werkzeug password hashing

## Object-Oriented Design
- **Abstraction:** abstract base class for content types (`models/recipe_models.py`)
- **Encapsulation:** private attributes exposed through properties
- **Inheritance:** `Creator` and `RegularUser` extend a base user class (`models/user_models.py`)
- **Factory pattern:** `UserFactory` creates the right user type

## Project Structure
```
app.py                  Flask routes and database setup
config.py               App configuration
models/                 User and recipe classes
templates/              HTML templates
static/uploads/         Uploaded recipe and profile images
migrate_favorites.py    Adds the favorites table to an older database
```

## Getting Started
1. Clone the repository and open the project folder.
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```
3. (Recommended) Set your own secret key:
   ```
   set SECRET_KEY=your-own-secret-key        # Windows
   export SECRET_KEY=your-own-secret-key     # macOS / Linux
   ```
4. Run the app. The database is created automatically on first run:
   ```
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

The app runs in debug mode, so it is meant for local development.

## Author
Amira Najihah Fadri Putri
Fidela Nabilah Putri Harinsi
Sulthania Auliya Afandi

<!-- If this was a team project, list the members and your role here. -->
