from app import app
from models import db, Video
import json

# create all table for initialization
with app.app_context():
    db.drop_all()
    db.create_all()

# Load intial video data
with open('/home/xb5/label_app/static/pairs.json', 'r') as file:
    data = json.load(file)

def insert_data(data):
    with app.app_context():
        for videoname, pairs in data.items():
            for pair in pairs:
                human1, human2 = pair
                video = Video(videoname=videoname, human1=human1, human2=human2)
                db.session.add(video)
        db.session.commit()

# Load the data
insert_data(data)
