# coding: UTF-8
# cornerDetection_Calib
# Akito Kosugi 
# ver.1.2    2019.11.13

# Import
import numpy as np
from pathlib import Path
import cv2
import os
import sys
import glob
import re
import tkinter
import tkinter.filedialog
from IPython.core.display import display

# Initialization
argv = sys.argv
cbrow = int(argv[1])
cbcol = int(argv[2])
num_cameras = int(argv[3])
cam_names = []
for cam in range(num_cameras):
    cam_names.append("camera-" + str(cam+1))

# Termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# Loading
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
img_path = tkinter.filedialog.askdirectory(initialdir = iDir)

images = glob.glob(os.path.join(img_path,'*.jpg'))

pathTemp = [os.path.dirname(img_path),'corners_all']
path_corners = os.path.join(*pathTemp)
os.makedirs(path_corners, exist_ok=True)
display(path_corners)

# Initialize the dictionary 
imgIdx = {}
for cam in cam_names:
    imgIdx.setdefault(cam,[])


# Sort the images
images.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
if len(images)==0:
    raise Exception("No calibration images found. Make sure the calibration images are saved as .jpg and with prefix as the camera name as specified in the config.yaml file.")

for fname in images:
    for cam in cam_names:
        if cam in fname:
            filename = Path(fname).stem

            regex = re.compile(r'-')
            splitTxt = regex.split(filename)
            regex = re.compile(r'_')
            splitTxt = regex.split(splitTxt[2])

            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (cbcol,cbrow),None,) #  (8,6) pattern (dimensions = common points of black squares)
            # If found, add object points, image points (after refining them)
            if ret == True:
                corners = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                # Draw the corners and store the images
                img = cv2.drawChessboardCorners(img, (cbcol,cbrow), corners,ret)
                cv2.imwrite(os.path.join(str(path_corners),filename+'_corner.jpg'),img)
                imgIdx[cam].append(int(splitTxt[0]))
            else:
                print("Corners not found for the image %s" %Path(fname).name)
display(imgIdx)


# Check unique images
if len(cam_names) == 2:
    uniqueIdx = list(set(imgIdx[cam_names[0]]) & set(imgIdx[cam_names[1]]))
elif len(cam_names) == 3:
    uniqueIdx = list(set(imgIdx[cam_names[0]]) & set(imgIdx[cam_names[1]]) & set(imgIdx[cam_names[2]]))
elif len(cam_names) == 4:
    uniqueIdx = list(set(imgIdx[cam_names[0]]) & set(imgIdx[cam_names[1]]) & set(imgIdx[cam_names[2]]) & set(imgIdx[cam_names[3]]))

display(uniqueIdx)


# Save unique images
pathTemp = [os.path.dirname(img_path),'calibration_images']
path_images = os.path.join(*pathTemp)
os.makedirs(path_images, exist_ok=True)
display(path_images)

for fname in images:
    for cam in cam_names:
        if cam in fname:
            idx = []
            filename = Path(fname).stem
            regex = re.compile(r'-')
            splitTxt = regex.split(filename)
            regex = re.compile(r'_')
            splitTxt = regex.split(splitTxt[2])
            idx.append((int(splitTxt[0])))

            if len(set(idx) & set(uniqueIdx)) > 0:
                img = cv2.imread(fname)
                cv2.imwrite(os.path.join(str(path_images),filename+'.jpg'),img)
