# filesProcessingExample
# Progarmmed by Akito Kosugi 
# ver.1.0    2019.10.12 <br>

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display


# Initialization

interval = 0
frameNum = 0
recFrameNum = 0
trialNum = 0
sumVal = 0
preSumVal = 0
addFrame = 0
startFrame = []
endFrame = []
duration = []

bRecording = False
bLED = False

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")


# Gamma conversion
gamma = 100
gamma_cvt = np.zeros((256,1), dtype=np.uint8)
for i in range(256):
    gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gamma/100)


# Define functions
def videoAnalysis(videofile_path):

    frameNum = 0
    interval = 0
    ESC_KEY = 0x1b # Esc キー
    S_KEY = 0x53 # s キー
    R_KEY = 0x52 # r キー

    fName = os.path.basename(os.path.splitext(videofile_path)[0])
    fNameExt = os.path.basename(os.path.splitext(videofile_path)[1])

    pathTemp = [os.path.dirname(os.path.splitext(videofile_path)[0]),fName + '_trimmed']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    pathTemp = [savePath,fName + "_trimmed_log.txt"]
    txtPath = os.path.join(*pathTemp)


    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ret, frame_1st = cap.read()
    frameNum += 1
    h, w, ch = frame_1st.shape
    frame_gamma_1st = cv2.LUT(frame_1st, gamma_cvt)

    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", w, h)
    cv2.imshow("Trimming",frame_1st)

    while(True):

        key = cv2.waitKey(interval)
        if key == ESC_KEY:
            break 
        elif key == R_KEY:
            interval = 0 
        elif key == S_KEY:
            interval = 30

        ret, frame = cap.read()
        frameNum += 1
        if ret == False:
            break
            
        if frameNum == 5:
            bRecording = True
            startFrame.append(frameNum)
            pathTemp = [savePath,"trimmed.jpg"]
            saveImgPath = os.path.join(*pathTemp)
            cv2.imwrite(saveImgPath,frame)
            break
        else:
            cv2.imshow("Trimming",frame)

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cmdText = 'Start frame: ' + str(startFrame)
    display(cmdText)
    display(saveImgPath)


# Open files
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
# files = tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir)
files = tkinter.filedialog.askopenfilenames(initialdir = iDir)
videoPath = list(files)

# Analysis
for i in range(len(files)):
    videoAnalysis(videoPath[i])
