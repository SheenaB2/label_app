# from flask import Flask, render_templates

from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Video, Label
from config import Config
from flask_migrate import Migrate
from sqlalchemy.sql import func
import random
import cv2
import csv

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Login Unsuccessful. Please check username and password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/index')
@login_required
def index():
    video = Video.query.first()  # Fetch your specific video
    bounding_box = get_first_bounding_box('static/Buenos_Aires_9.txt')
    return render_template('index.html', video=video, bounding_box=bounding_box)

@app.route('/submit_result', methods=['POST'])
@login_required
def submit_result():
    video_id = request.form['video_id']
    result = request.form['result'] == 'yes'
    
    # Save the result to the database
    new_result = Label(user_id=current_user.id, video_id=video_id, label=result)
    db.session.add(new_result)
    db.session.commit()
    
    return redirect(url_for('index'))

def get_first_bounding_box(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            return {
                'x': float(row[2]),
                'y': float(row[3]),
                'width': float(row[4]),
                'height': float(row[5])
            }
    return None

if __name__ == "__main__":
    app.run(debug=True)
