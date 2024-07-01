# from flask import Flask, render_templates

from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory,Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Video, Label
from config import Config
from flask_migrate import Migrate
from sqlalchemy.sql import func
import random
import cv2



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

# @app.route('/index')
# @login_required
# def index():
#     labeled_videos = Label.query.filter_by(user_id=current_user.id).all()
#     labeled_video_ids = [label.video_id for label in labeled_videos]
#     # videos = Video.query.filter(~Video.id.in_(labeled_video_ids)).limit(10).all()
#     videos = Video.query.filter(~Video.id.in_(labeled_video_ids)).order_by(func.random()).limit(10).all()
#     return render_template('index.html', videos=videos)

# @app.route('/label/<int:video_id>', methods=['POST'])
# @login_required
# def label(video_id):
#     label = request.form['label']
#     new_label = Label(user_id=current_user.id, video_id=video_id, label=label)
#     db.session.add(new_label)
#     db.session.commit()
#     return redirect(url_for('index'))

def draw_boxes(img,box1,box2,label1,label2):
    box_color = (0, 255, 0)  # Green color
    box_thickness = 2

    if box1 != []:
      c1, c2 = (int(box1[0]), int(box1[1])), (int(box1[0]+box1[2]), int(box1[1]+box1[3]))
      cv2.rectangle(img, c1, c2, box_color, box_thickness)
      cv2.putText(img, label1, (c1[0], c1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)

    if box2 != []:
      c1, c2 = (int(box2[0]), int(box2[1])), (int(box2[0]+box2[2]), int(box2[1]+box2[3]))
      cv2.rectangle(img, c1, c2, box_color, box_thickness)
      cv2.putText(img, label2, (c1[0], c1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)

def generate_frames(video_path, file_path, target_1, target_2):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    data_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Assuming the format is {frame},{id},{x1},{y1},{w},{h},{s},-1,-1,-1
                parts = line.strip().split(',')

                # Extracting values
                frame = int(parts[0])
                id = int(parts[1])
                box = [float(part) for part in parts[2:6]]
                # if id in count.keys():
                # count[id] += 1
                # else:
                # count[id] = 1

                # Creating dictionary entry
                if frame in data_dict.keys():
                    data_dict[frame][id] = box
                else:
                    data_dict[frame] = {id:box}

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    current_frame = 1
    while cap.isOpened() and current_frame <= 150:
        ret, frame = cap.read()
        if not ret:
            break

        # Draw bounding boxes for each frame
        for frameNum, info in data_dict.items():
            if frameNum == current_frame:
                box1 = info.get(int(target_1), [])
                box2 = info.get(int(target_2), [])
                # print(box1,box2)
                draw_boxes(frame, box1, box2, str(target_1), str(target_2))
                break

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        current_frame += 1

    cap.release()

@app.route('/video_feed')
def video_feed():
    # Example video path and data_dict for demonstration purposes
    # video_path = '/home/xb5/label_app/static/Amsterdam_0.mp4'
    # file_path = '/home/xb5/label_app/static/Amsterdam_0.txt'
    # target_1 = 12
    # target_2 = 13

    video_path = request.args.get('video_path')
    file_path = request.args.get('file_path')
    target_1 = request.args.get('target_1')
    target_2 = request.args.get('target_2')

    return Response(generate_frames(video_path, file_path, target_1, target_2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/index')
@login_required
def index():
    labeled_videos = Label.query.filter_by(user_id=current_user.id).all()
    labeled_video_ids = [label.video_id for label in labeled_videos]
    videos = Video.query.filter(~Video.id.in_(labeled_video_ids)).order_by(func.random()).limit(10).all()
    return render_template('index.html', videos=videos)

@app.route('/submit_result', methods=['POST'])
@login_required
def submit_result():
    # video_id = request.form['video_id']
    video_id = request.args.get('video_id')
    print(video_id)
    result = request.form['result'] == 'yes'
    
    # Save the result to the database
    new_result = Label(user_id=current_user.id, video_id=video_id, label=result)
    db.session.add(new_result)
    db.session.commit()
    
    # # Determine the next video index
    # current_video_index = int(request.form['current_video_index']) + 1
    
    # labeled_videos = Label.query.filter_by(user_id=current_user.id).all()
    # labeled_video_ids = [label.video_id for label in labeled_videos]
    # videos = Video.query.filter(~Video.id.in_(labeled_video_ids)).order_by(func.random()).all()
    
    # if current_video_index < len(videos):
    #     return render_template('index.html', videos=videos, current_video_index=current_video_index)
    # else:
    #     return "All videos reviewed"


if __name__ == "__main__":
    app.run(debug=True)
