import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import cv2
import numpy as np
from keras.models import load_model
import cv2
import os

classification_model = load_model("./yoga3.h5")

def detect_img(yolo):
	frames_folder = "./data/vid_000601032019/"
	frames = os.listdir(frames_folder)
	frames.sort()
	timing_file = "./data/vid_000601032019_log.txt"
	#begin reading timing file
	raw_ts = []
	with open(timing_file) as fp:
	    for line in fp:
	    	raw_ts.append(line.rstrip("\n"))
	timestamps = []
	for ts in raw_ts:
		ts = ts.split(":")[1]
		timestamps.append(ts)
	#end file reading
	predicted_pose_sequence = []
	for frame in frames:
		img = "./data/vid_000601032019/"+frame
		try:
		    image = Image.open(img)
		except:
		    print('Open Error! Try again!')
		    continue
		else:
		    od_data = yolo.detect_image(image)
		    if od_data == 0:
		    	predicted_pose_sequence.append("none")
		    elif od_data == -1:
		    	predicted_pose_sequence.append("many")
		    else:
		        crop_coord = od_data[0]
		        obj_accuracy = od_data[1]
		        x1 = crop_coord[0][0]
		        y1 = crop_coord[0][1]
		        x2 = crop_coord[0][2]
		        y2 = crop_coord[0][3]
		        cropped_im = np.array(image.crop((x1,y1,x2,y2)))
		        predicted_pose = classify_pose(cropped_im)
		        predicted_pose_sequence.append(predicted_pose)
	description = build_description(predicted_pose_sequence, timestamps)

	yolo.close_session()

def classify_pose(cropped_im):
	cropped_im = cv2.resize(cropped_im,(224,224))
	cropped_im = np.reshape(cropped_im,(1,224,224,3))
	predictions = classification_model.predict(cropped_im)
	return(np.argmax(predictions))

def build_description(predicted_pose_sequence,timestamps):
	description = ""
	# for p,t in zip(predicted_pose_sequence,timestamps):
	# 	print(p,t)
	ideal_pose_sequence = "012345643210" #represents complete suryanamaskar
	current_sequence = str(predicted_pose_sequence[0])
	for pose in predicted_pose_sequence:
		if pose=="many" or pose=="none" or pose==int(current_sequence[-1]):
			continue
		else:
			current_sequence+=str(pose)
	print(current_sequence)
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
