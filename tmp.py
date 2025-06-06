import numpy as np
import cv2

# 创建一个模拟的640x480的图片，使用OpenCV格式
image = cv2.imread('./tmp.jpg')
x = 0
y = 0
roi_x = 307
roi_y = 111
roi_length = 152

piece = image[roi_y+x*roi_length//3:roi_y+x*roi_length//3+roi_length//3, roi_x+y*roi_length//3:roi_x+y*roi_length//3+roi_length//3]

cv2.imshow('1', piece)
cv2.waitKey(0)
cv2.destroyAllWindows()