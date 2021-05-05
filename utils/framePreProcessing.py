"""
coding: UTF-8
movie trimming utils
# by Akito Kosugi 
# ver. 1.1   2020.12.29

"""

# Import
import cv2
import numpy as np

def gammaConv(img, gammaVal):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 

    return img_gamma

def preProcessing(img,rot_angle,gammaVal):
    # Rotation
    if rot_angle == 270:
        img_rot = cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rot_angle == 90:
        img_rot= cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
    elif rot_angle == 180:
        img_rot= cv2.rotate(img,cv2.ROTATE_180)
    else:
        img_rot = img.copy()
    # Gamma conv
    img_process = gammaConv(img_rot,gammaVal)
    
    return img_process