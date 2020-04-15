# frameRejection_Calib.py
# Akito Kosugi 
# ver.1.0    2020.04.07

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

images = glob.glob(os.path.join(img_path,'*.jpg'))

root = tkinter.Tk()
root.withdraw()
fTyp = [("","*csv")]
iDir = os.path.abspath(os.path.dirname('__file__'))
csvPath = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
csvName = os.path.basename(os.path.splitext(csvPath)[0])

display(csvPath)

csv_input = pd.read_csv(csvPath)
row,col = csv_input.shape
display(str(csv_input.values))
display(str(row))
display(str(col))

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
	imgIdx.append(regex.split(splitTxt[1]))
	j += 1
	display(imgIdx[j])	

	if imgIdx[j] == csv_input.values[0,i]:
		display(csv_input.values[0,i])		
	else:
		i += 1
		img = cv2.imread(fname)
		cv2.imwrite(os.path.join(str(saveFolder),filename+'.jpg'),img)