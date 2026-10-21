from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import sqlite3
from models.user_models import UserFactory, Creator, RegularUser
from models.recipe_models import Recipe, RecipeManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def init_db():
    conn = sqlite3.connect('recipe_book.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER,
                    recipe_id INTEGER,
                    PRIMARY KEY (user_id, recipe_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
                )''')

    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  user_type TEXT NOT NULL,
                  profile_image TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  ingredients TEXT NOT NULL,
                  instructions TEXT NOT NULL,
                  category TEXT NOT NULL,
                  cooking_time INTEGER,
                  servings INTEGER,
                  image_path TEXT,
                  creator_id INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (creator_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    recipe_manager = RecipeManager()
    recipes = recipe_manager.get_all_recipes()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('creator_dashboard' if session['user_type'] == 'creator' else 'user_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        user_factory = UserFactory()
        user = user_factory.create_user(user_type, username, email, password)
        
        if user.save():
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username atau email sudah digunakan!', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('creator_dashboard' if session['user_type'] == 'creator' else 'user_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[3], password):
            session['user_id'] = user_data[0]
            session['username'] = user_data[1]
            session['user_type'] = user_data[4]

            
            if user_data[4] == 'creator':
                return redirect(url_for('creator_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recipe_manager = RecipeManager()
    recipes = recipe_manager.get_all_recipes()
    return render_template('user_dashboard.html', recipes=recipes)

@app.route('/favorites')
def favorites():
    if 'user_id' not in session or session['user_type'] != 'user':
        flash("Anda harus login sebagai pengguna biasa untuk melihat favorit.", "error")
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('recipe_book.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.*, u.username 
        FROM recipes r 
        JOIN users u ON r.creator_id = u.id
        JOIN favorites f ON r.id = f.recipe_id
        WHERE f.user_id = ?
        ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    favorite_recipes = c.fetchall()
    conn.close()

    return render_template('favorites.html', recipes=favorite_recipes)


@app.route('/creator_dashboard')
def creator_dashboard():
    if 'user_id' not in session or session['user_type'] != 'creator':
        return redirect(url_for('login'))
    
    recipe_manager = RecipeManager()
    my_recipes = recipe_manager.get_recipes_by_creator(session['user_id'])
    return render_template('creator_dashboard.html', recipes=my_recipes)

@app.route('/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    if 'user_id' not in session or session['user_type'] != 'creator':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        category = request.form['category']
        cooking_time = int(request.form['cooking_time']) if request.form['cooking_time'] else None
        servings = int(request.form['servings']) if request.form['servings'] else None
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                image_path = filename  
        
        recipe = Recipe(title, description, ingredients, instructions, category, 
                       cooking_time, servings, image_path, session['user_id'])
        
        if recipe.save():
            flash('Resep berhasil dibuat!', 'success')
            return redirect(url_for('creator_dashboard'))
        else:
            flash('Terjadi kesalahan saat membuat resep!', 'error')
    
    return render_template('create_recipe.html')

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if 'user_id' not in session or session['user_type'] != 'creator':
        flash('Anda tidak memiliki izin untuk menghapus resep ini.', 'error')
        return redirect(url_for('login'))
    
    recipe_manager = RecipeManager()
    success = recipe_manager.delete_recipe(recipe_id, session['user_id'])

    if success:
        flash('Resep berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus resep. Anda hanya dapat menghapus resep milik Anda.', 'error')

    return redirect(url_for('creator_dashboard'))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    recipe_manager = RecipeManager()
    recipes = recipe_manager.search_recipes(query, category)
    
    return render_template('search_results.html', recipes=recipes, query=query, category=category)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe_manager = RecipeManager()
    recipe = recipe_manager.get_recipe_by_id(recipe_id)
    
    if not recipe:
        flash('Resep tidak ditemukan!', 'error')
        return redirect(url_for('index'))
    
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['image']
    if file and file.filename:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = f"profile_{timestamp}{filename}"
        
        upload_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        print("DEBUG: Upload to", filepath) 
        file.save(filepath)
        
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('UPDATE users SET profile_image = ? WHERE id = ?', (filename, session['user_id']))
        conn.commit()
        conn.close()

        session['profile_image'] = filename
        
        return jsonify({'success': True, 'filename': filename})
    
    return jsonify({'success': False, 'message': 'Invalid file'})

@app.route('/favorite/<int:recipe_id>', methods=['POST'])
def favorite(recipe_id):
    if 'user_id' not in session or session['user_type'] != 'user':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('recipe_book.db')
    c = conn.cursor()
    flash('Resep sudah ada di favorit.', 'info')
    try:
        c.execute('INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)', (session['user_id'], recipe_id))
        conn.commit()
        flash('Resep sudah ada di favorit.', 'info')
    except sqlite3.IntegrityError:
        flash('Resep sudah ada di favorit.', 'info')
    conn.close()
    return redirect(request.referrer or url_for('user_dashboard'))

@app.route('/unfavorite/<int:recipe_id>', methods=['POST'])
def unfavorite(recipe_id):
    if 'user_id' not in session or session['user_type'] != 'user':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('recipe_book.db')
    c = conn.cursor()
    c.execute('DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?', (session['user_id'], recipe_id))
    conn.commit()
    conn.close()
    flash('Resep sudah dihapus dari favorit.', 'info')
    return redirect(request.referrer or url_for('user_dashboard'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(debug=True)