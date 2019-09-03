import os
import cv2 as cv
import numpy as np
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField
from stickynotes import board, postits, object_detector

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads
app.config['PATH_TO_FROZEN_GRAPH'] = 'data/frozen_inference_graph.pb'
app.config['PATH_TO_LABELS'] = 'data/stickynote.pbtxt'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


class UploadForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Your username.."})
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    email = StringField('Trello email address', validators=[DataRequired()], render_kw={"placeholder": "Your email.."})
    submit = SubmitField('Upload')

detector = object_detector.Detector(app.config['PATH_TO_FROZEN_GRAPH'], app.config['PATH_TO_LABELS'])

def board_from_image(file, name, email):
    bgr = cv.imdecode(np.frombuffer(file.read(), np.uint8), -1)
    image = cv.cvtColor(bgr, cv.COLOR_BGR2RGB)
    postits.postit_board(detector, 'a board', image, name, email)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        board_from_image(form.photo.data, form.name.data, form.email.data)
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run()