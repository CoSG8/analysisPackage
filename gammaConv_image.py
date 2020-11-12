# coding: UTF-8
# gammaConv_image
# Akito Kosugi
# ver.1.1    2019.12.22

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
gamma = 1

def onTrackbar(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st.copy())
    cv2.imshow("Trimming",frame_1st_disp)
    display("Gamma : " +  str(gamma))
    
# Define Gamma conversion
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt)
    return img_gamma

# Main
# Open files
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
# for Win
# files = tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir)
# for Mac
files = tkinter.filedialog.askopenfilenames(initialdir = iDir)
imgPath = list(files)

# Analysis
for i in range(len(files)):
    fName = os.path.basename(os.path.splitext(imgPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(imgPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(imgPath[i])[0]),fName + '_gammaConv']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)

    img = cv2.imread(imgPath[i])
    h, w, ch = img.shape
    
    # window setting
    cv2.namedWindow("Gamma", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Gamma", w, h)
    cv2.imshow("Gamma", img)
    cv2.waitKey(0)
