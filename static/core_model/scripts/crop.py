from PIL import Image
im_name = input("File Name : ")
crop_p = (10,52,440,385)
img = Image.open(im_name)
img = img.crop(crop_p)
img.show()