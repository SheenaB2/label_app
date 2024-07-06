from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    videoname = db.Column(db.String(100), nullable=False)
    human1 = db.Column(db.Integer, nullable=False)
    human2 = db.Column(db.Integer, nullable=False)

class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    label = db.Column(db.Integer, nullable=False)  
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id', name='unique_user_video'),)
