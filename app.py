# from flask import Flask, render_templates

from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory,Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Video, Label
from config import Config
from flask_migrate import Migrate
from sqlalchemy.sql import func
from flask_cors import CORS
import os
from dotenv import load_dotenv



app = Flask(__name__)
CORS(app)
# app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')
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
            return redirect(url_for('home'))
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
    labeled_videos = Label.query.filter_by(user_id=current_user.id).all()
    labeled_video_ids = [label.video_id for label in labeled_videos]
    videos = Video.query.filter(~Video.id.in_(labeled_video_ids)).order_by(func.random()).all()
    current_video_index = request.args.get('current_video_index', default=0, type=int)
    return render_template('index.html', videos=videos, current_video_index=current_video_index)

@app.route('/submit_result', methods=['POST'])
@login_required
def submit_result():
    video_id = request.form['video_id']
    result = request.form['result']
    
    # Save the result to the database
    new_result = Label(user_id=current_user.id, video_id=video_id, label=result)
    db.session.add(new_result)
    db.session.commit()
    
    # Determine the next video index
    current_video_index = int(request.form['current_video_index']) + 1
        
    if current_video_index < 10:
        return redirect(url_for('index', current_video_index=current_video_index))
    else:
        return render_template('finish.html')

if __name__ == "__main__":
    app.run()
