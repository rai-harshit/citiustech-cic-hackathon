from PIL import Image
import numpy as np
import cv2

def make_square(im, min_size=256, fill_color=(0, 0, 0)):
    x, y = im.size
    print(x,y)
    size = max(min_size, x, y)
    print(size)
    new_im = Image.new('RGB', (size, size), fill_color)
    new_im.paste(im, (int((size - x) / 2), int((size - y) / 2)))
    return new_im

test_image = Image.open('dh.jpg')
new_image = make_square(test_image)
new_image = np.array(new_image)
new_image = cv2.resize(new_image,(224,224))
cv2.imwrite("lavda.jpg",new_image)