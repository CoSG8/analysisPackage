# coding: UTF-8
# frameRejection_Calib.py
# Akito Kosugi 
# ver.1.0.1    2020.04.18

# Import
import cv2
import math
import sys
import os
import glob
import re
import tkinter
import tkinter.filedialog
import pandas as pd
import numpy as np
from pathlib import Path
from IPython.core.display import display


# Loading

root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
img_path = tkinter.filedialog.askdirectory(initialdir = iDir)

display(img_path)

images = glob.glob(os.path.join(img_path,'*.jpg'))

root = tkinter.Tk()
root.withdraw()
fTyp = [("","*csv")]
iDir = os.path.abspath(os.path.dirname('__file__'))
csvPath = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
csvName = os.path.basename(os.path.splitext(csvPath)[0])

display(csvPath)

csv_input = pd.read_csv(csvPath, header=None)
csv_input_values =list(csv_input.values)
display(str(csv_input_values))

pathTemp = [os.path.dirname(os.path.splitext(csvPath)[0]),'calibration_images']
saveFolder = os.path.join(*pathTemp)
os.makedirs(saveFolder, exist_ok=True)

# Initialize the dictionary 
imgIdx = []
# for cam in cam_names:
#     imgIdx.setdefault(cam,[])

i = 1
j = -1
for fname in images:

	filename = Path(fname).stem
	regex = re.compile(r'-')
	splitTxt = regex.split(filename)
	regex = re.compile(r'_')
	imgIdx.append(regex.split(splitTxt[2]))
	j += 1
	# display('imgIdx: ' + str(imgIdx[j]))

	if len(set(imgIdx[j]) & set(csv_input_values)) > 0:
		display('imgIdx: ' + str(imgIdx[j]))
		img = cv2.imread(fname)
		cv2.imwrite(os.path.join(str(saveFolder),filename+'.jpg'),img)
