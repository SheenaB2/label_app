# Walking Tour Video Labeling Web Application
This web application is designed for labeling walking tour videos, where users can sign in and label whether people in the video belong to the same "group" or not. This labeling process helps in analyzing the behavior and interactions of people in various walking tours.

# Setup Instructions
Prerequisites
- Python 3.x
- pip (Python package installer)
- SQLite
  
Installation
- `git clone https://github.com/SheenaB2/label-app`
  
Create and activate a virtual environment (Install python and pip first if you haven't done so)
- `python3 -m venv venv`
- `source venv/bin/activate`  (On Windows: `venv\Scripts\activate`)
- `pip install Flask`
- `pip install Flask-SQLAlchemy`

Initialize database:
- `python init.py`

Run application:
- `python app.py`
