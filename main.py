#

import logging
import os
from flask import Flask, request, jsonify
from flask import render_template,Markup
import json
from flask import redirect, send_from_directory
from werkzeug.utils import secure_filename
import base64
import json
import cv2
import os
import glob
if 'DYNO' in os.environ:
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)

# UPLOAD_FOLDER = '/home/ultron/Desktop/Hackathon/app-engine-master/uploads'
UPLOAD_FOLDER ="static/img/uploads"
DISPLAY_FOLDER="static/img/display"
FRAME_FOLDER="static/img/frames"
ALLOWED_EXTENSIONS = set(['png','jpg','mp4', 'avi'])
app = Flask(__name__, static_url_path="", static_folder="static")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
	return render_template("index.html")

@app.route('/upload',methods=['POST'])
def upload():
	file=request.files["input_file"]
	files = glob.glob(UPLOAD_FOLDER+'/*')
	for f in files:
		os.remove(f)
	files = glob.glob(DISPLAY_FOLDER+'/*')
	for f in files:
		os.remove(f)
	files = glob.glob(FRAME_FOLDER+'/*')
	for f in files:
		os.remove(f)
	if(file.filename==''):
		return "file not selected"
	if file and allowed_file(file.filename):
		filename=secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		# x=cv2.imread(UPLOAD_FOLDER+filename)
		# with open("static/img/uploads/"+"2.jpg", "rb") as imageFile:
		# 	str1 = base64.b64encode(imageFile.read())
		# 	print(str1)
		# k=send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)
		# # print(jsonify(k))
		# print(filename)
		# p=cv2.imread(UPLOAD_FOLDER+"/"+file)
		# encode_string=base64.b64encode(p)
		# print(p)
		for i in os.listdir(UPLOAD_FOLDER):
			os.system('ffmpeg -i {} -vf select=key -an -vsync 0 ./static/img/frames/%d.jpeg -loglevel debug 2>&1 | grep select:1'.format("./"+UPLOAD_FOLDER+"/"+i))
			os.system('ffprobe -v error -skip_frame nokey -show_entries frame=pkt_pts_time -select_streams v -of csv=p=0 {} > ./static/img/timestamp.txt'.format("./"+UPLOAD_FOLDER+"/"+i))
			os.system('python ./static/core_model/yolo_video.py --image')
		raw_ts = []
		with open('./static/img/timestamp.txt') as fp:
			for line in fp:
				raw_ts.append(float(line.rstrip("\n")))
		# print(raw_ts)
		f=open("./static/description.txt","r")
		desc=f.read()
		f.close()
		x='''
		<head>
		  <link rel="shortcut icon"
		    href="{{ url_for('static', filename='img/favicon.ico') }}">
		  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
		  <meta charset="utf-8">
		  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		  <meta name="description" content="">
		  <meta name="author" content="">

		  <title>YOGA</title>
		  <style type="text/css">
		    #input_file { visibility: hidden; }
		  </style>

		  <!-- Font Awesome Icons -->
		  <link href="vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">

		  <!-- Google Fonts -->
		  <link href="https://fonts.googleapis.com/css?family=Merriweather+Sans:400,700" rel="stylesheet">
		  <link href='https://fonts.googleapis.com/css?family=Merriweather:400,300,300italic,400italic,700,700italic' rel='stylesheet' type='text/css'>

		  <!-- Plugin CSS -->
		  <link href="vendor/magnific-popup/magnific-popup.css" rel="stylesheet">

		  <!-- Theme CSS - Includes Bootstrap -->
		  <link href="css/creative.min.css" rel="stylesheet">
		   <link href="css/display.css" rel="stylesheet">

		</head>  
			 <section class="page-section" id="services">
			    <div class="container">
			      <h2 class="text-center mt-0">Surya Namaskar Pose Detection Summary</h2>
			      <hr class="divider my-4">
		      <div class="row"> 

		'''
		x=x+"<b>"+desc+"</b>"
		# y=''''''
		# for i in (os.listdir(DISPLAY_FOLDER)):
		# 	y=y+'''<div class="col-lg-3 col-md-6 text-center">
  #         <div class="mt-5">
  #           <img src="/img/display/'''+i+'''" />
  #           <h3 class="h4 mb-2">'''+i+'''</h3>
  #         </div>
  #       </div>'''
		z='''
            </div>
			  </section>
        '''
		tab='''
				<section class="page-section" id="services">
			    <table>
				  <tr>
				    <th><center>Image</center></th>
				    <th><center>Description</center></th>
				    </th>
				   </tr>

        '''
		name=['Pranamasana','Hastha Uttanasana','Padahastasana','Ashwa Sanchalanasana','Parvatasana','Bhujangasana','Ashtanga Namaskara']
		frames_folder =  "./static/img/frames/"
		frames_str = os.listdir(frames_folder)
		frames_int = []
		frames = []
		prediction=[]
		timing_file ="./static/prediction.txt"
		with open(timing_file) as fp:
		    for line in fp:
		    	prediction.append(line.rstrip("\n"))
		for f in frames_str:
			num = int(f.split(".")[0])
			frames_int.append(num)
		frames_int.sort()
		for f in frames_int:
			frames.append(str(f)+".jpeg")
		for i in range(len(frames)):
				p=int(prediction[i])
				tab1="None"
				if p==-2:
					tab1="None"
				else:
					tab1=name[p]
				tab=tab+'''<tr>
				<td><center><img src="/img/frames/{}" style="width:200px;height:150px"></img></center></td>
				<td><center><b>The pose identified in the frame is: {}</b></center></td>
				</tr>'''.format(frames[i],tab1)

		tab=tab+'''</table></section>'''
		page=x+z+tab
		# message = Markup("<link href=\"css/display.css\" rel=\"stylesheet\"><div class=\"row\"> <div class=\"column\"><img src=\"/img/uploads/2.jpg\" style=\"width:100%\"></div><div class=\"column\"><img src=\"/img/uploads/2.jpg\" style=\"width:100%\"></div><div class=\"column\"><img src=\"/img/uploads/2.jpg\" style=\"width:100%\"></div></div>")
		message=Markup(page)
		return message
		# return "upload`oaded Successfully"
	else:
		return "Not Supported filename"

@app.route('/view')
def view():
	x=cv2.imread(UPLOAD_FOLDER+"/"+"1.jpg")
	print(x)
	message = Markup("<h1>Voila! Platform is ready to used</h1>")
	return message
@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
if __name__ == '__main__':
	app.run(debug=True)
