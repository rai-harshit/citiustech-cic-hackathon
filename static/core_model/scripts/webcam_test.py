import cv2
import numpy as np
import keras
from keras.models import load_model
import time

model_file = "./yoga3.h5"
load_start = time.time()
model = load_model(model_file)
load_end = time.time()
print("Took {} seconds to load model".format(load_end-load_start))
trigger = input("Press Enter to Begin")

load_time = []

cap = cv2.VideoCapture(0)
count=0
while(True):
	ret,frame = cap.read()
	img = cv2.resize(frame,(224,224))
	img = np.reshape(img,(1,224,224,3))
	# start = time.time()
	prediction = model.predict(img)
	print(prediction)
	# end = time.time()
	# load_time.append(end-start)
	cv2.imshow("GrayScale Video",frame)	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cap.release()
cv2.destroyAllWindows()
total_delay = 0
# for t in load_time:
# 	total_delay+=t
# print("Total Delay Points : {}".format(len(load_time)))
# print("Sum of Delay Times : {}".format(total_delay))
# print("Average Delay Time : {}".format(total_delay/len(load_time)))
