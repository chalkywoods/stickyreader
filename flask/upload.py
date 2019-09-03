import os
import cv2 as cv
import numpy as np
from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import SubmitField, StringField
from stickynotes import board, postits, object_detector, azure

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')
app.config['PATH_TO_FROZEN_GRAPH'] = 'data/frozen_inference_graph.pb'
app.config['PATH_TO_LABELS'] = 'data/stickynote.pbtxt'
app.config['AZURE_ENDPOINT'] = 'https://stickynote.cognitiveservices.azure.com/vision/v2.0/read/core/asyncBatchAnalyze'
app.config['AZURE_KEY'] = '26a32a30c1bd44c1b73dd5827bcc5a13'
app.config['TRELLO_TOKEN'] = '56527009f8e75488442c4d88417af348c86e32e03d2852286f0d0fe580c45051'
app.config['TRELLO_KEY'] = '3e45014c6465df422ec100f100892125'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

class UploadForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Your username.."})
    photo = FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    email = StringField('Trello email address', validators=[DataRequired()], render_kw={"placeholder": "Your email.."})
    submit = SubmitField('Upload')

detector = object_detector.Detector(app.config['PATH_TO_FROZEN_GRAPH'], app.config['PATH_TO_LABELS'])
text_detector = azure.TextDetector(app.config['AZURE_KEY'], app.config['AZURE_ENDPOINT'])

def board_from_image(file, name, email):
    bgr = cv.imdecode(np.frombuffer(file.read(), np.uint8), -1)
    image = cv.cvtColor(bgr, cv.COLOR_BGR2RGB)
    return postits.postit_board(detector, text_detector, app.config['TRELLO_KEY'], app.config['TRELLO_TOKEN'], 'a board', image, name, email)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    url = None
    if form.validate_on_submit():
        url = board_from_image(form.photo.data, form.name.data, form.email.data)
    return render_template('index.html', form=form, url=url)

if __name__ == '__main__':
    app.run()