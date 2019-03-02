import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import cv2
import numpy as np
from keras.models import load_model
import cv2
import os

classification_model = load_model("./static/core_model/yoga7.h5")

def detect_img(yolo):
	frames_folder = "./static/img/frames"
	frames_str = os.listdir(frames_folder)
	frames_int = []
	frames = []
	for f in frames_str:
		num = int(f.split(".")[0])
		frames_int.append(num)
	frames_int.sort()
	for f in frames_int:
		frames.append(str(f)+".jpeg")
	print(frames)

	timing_file = "./static/img/timestamp.txt"
	#begin reading timing file
	raw_ts = []
	with open(timing_file) as fp:
	    for line in fp:
	    	raw_ts.append(line.rstrip("\n"))
	timestamps = raw_ts
	# for ts in raw_ts:
	# 	ts = ts.split(":")[1]
	# 	timestamps.append(ts)
	#end file reading
	predicted_pose_sequence = []
	# while True:
	for frame in frames:
		img = "./static/img/frames/"+frame
		try:
		    image = Image.open(img)
		except:
		    print('Open Error! Try again!')
		    continue
		else:
			if ".png" in frame:
		  	    image = image.convert('RGB')
			od_data = yolo.detect_image(image)
			# od_data.show()
			if od_data == 0:
				predicted_pose_sequence.append(-2)
			elif od_data == -1:
				predicted_pose_sequence.append(-1)
			else:
				crop_coord = od_data[0]
				obj_accuracy = od_data[1]
				x1 = crop_coord[0][0]
				y1 = crop_coord[0][1]
				x2 = crop_coord[0][2]
				y2 = crop_coord[0][3]
				cropped_im = image.crop((y1,x1,y2,x2))
				padded_image = pad_image(cropped_im)
				# padded_image.save("./save/"+frame)
				predicted_pose = classify_pose(np.array(padded_image),frame)
				predicted_pose_sequence.append(predicted_pose)
	print(predicted_pose_sequence)
	description = build_description(predicted_pose_sequence, timestamps)

	yolo.close_session()

def pad_image(cropped_im, min_size=256, fill_color=(0, 0, 0)):
	x,y = cropped_im.size
	size = max(min_size, x, y)
	new_im = Image.new('RGB', (size, size), fill_color)
	new_im.paste(cropped_im, (int((size - x) / 2), int((size - y) / 2)))
	return new_im

def classify_pose(cropped_im,frame):
	cropped_im = cv2.resize(cropped_im,(224,224))
	cropped_im = np.reshape(cropped_im,(1,224,224,3))
	predictions = classification_model.predict(cropped_im)
	print(frame,np.argmax(predictions))
	return(np.argmax(predictions))

def build_description(predicted_pose_sequence,timestamps):
	description = ""
	ideal_pose_sequence = "012345643210" #represents complete suryanamaskar
	current_sequence = [predicted_pose_sequence[0]]
	for pose in predicted_pose_sequence:
		if pose==-1 or pose==-2:
			continue
		elif pose==int(current_sequence[-1]):
			continue
		else:
			current_sequence.append(pose)
	# print(current_sequence)
	return description

FLAGS = None

if __name__ == '__main__':
    # class YOLO defines the default value, so suppress any default here
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    '''
    Command line options
    '''
    parser.add_argument(
        '--model', type=str,
        help='path to model weight file, default ' + YOLO.get_defaults("model_path")
    )

    parser.add_argument(
        '--anchors', type=str,
        help='path to anchor definitions, default ' + YOLO.get_defaults("anchors_path")
    )

    parser.add_argument(
        '--classes', type=str,
        help='path to class definitions, default ' + YOLO.get_defaults("classes_path")
    )

    parser.add_argument(
        '--gpu_num', type=int,
        help='Number of GPU to use, default ' + str(YOLO.get_defaults("gpu_num"))
    )

    parser.add_argument(
        '--image', default=False, action="store_true",
        help='Image detection mode, will ignore all positional arguments'
    )
    '''
    Command line positional arguments -- for video detection mode
    '''
    parser.add_argument(
        "--input", nargs='?', type=str,required=False,default='./path2your_video',
        help = "Video input path"
    )

    parser.add_argument(
        "--output", nargs='?', type=str, default="",
        help = "[Optional] Video output path"
    )

    FLAGS = parser.parse_args()

    if FLAGS.image:
        """
        Image detection mode, disregard any remaining command line arguments
        """
        print("Image detection mode")
        if "input" in FLAGS:
            print(" Ignoring remaining command line arguments: " + FLAGS.input + "," + FLAGS.output)
        detect_img(YOLO(**vars(FLAGS)))
    elif "input" in FLAGS:
        detect_video(YOLO(**vars(FLAGS)), FLAGS.input, FLAGS.output)
    else:
        print("Must specify at least video_input_path.  See usage with --help.")
