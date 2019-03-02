import numpy as np
import cv2
from keras.models import load_model
model = load_model("yoga3.h5")

img_name = input("File Name : ")
img = cv2.imread(img_name)
img = cv2.resize(img,(224,224))
img = np.reshape(img,(1,224,224,3))
prediction = model.predict(img)
print(prediction)