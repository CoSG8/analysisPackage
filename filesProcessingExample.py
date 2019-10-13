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
recFrameNum = 0
trialNum = 0

addFrame = 0
gamma = 1
searchColor = 1
ledTh = 100

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")


# Define functions
def checkLEDPos(videofile_path):
    frameNum = 0
    interval = 0
    ESC_KEY = 0x1b # Esc キー
    S_KEY = 0x53 # s キー
    R_KEY = 0x52 # r キー
    global frame_1st

    fName = os.path.basename(os.path.splitext(videofile_path)[0])
    fNameExt = os.path.basename(os.path.splitext(videofile_path)[1])

    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ret, frame_1st = cap.read()
    frameNum += 1
    h, w, ch = frame_1st.shape
 
    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", w, h)
    cv2.imshow("Trimming",frame_1st)
    cv2.setMouseCallback("Trimming",get_position)
    cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
    cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar2)
    cv2.createTrackbar("Color","Trimming",searchColor,2,onTrackbar3)

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
        if frameNum > 1:
            break
            cv2.waitKey(1)    
            cv2.destroyAllWindows()
            cv2.waitKey(1)


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX, roiY, roiW, roiH
        roiW = 20
        roiH = 20
        roiX = x - int(roiW/2)
        roiY = y - int(roiH/2)
        print((roiX,roiY))
        frame_1st_disp  = gammaConv(gamma,frame_1st.copy())
        cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.imshow("Trimming",frame_1st_disp)


# Define trackbar
def onTrackbar1(position):
    global ledTh
    ledTh = position
    display("LED Th: " +  str(ledTh))

def onTrackbar2(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st.copy())
    cv2.imshow("Trimming",frame_1st_disp)
    display("Gamma : " +  str(gamma))


def onTrackbar3(position):
    global searchColor
    searchColor = int(position)
    display("Color: " + str(searchColor)) 


# Define Gamma conversion
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma


def videoAnalysis(videofile_path):
    startFrame = []
    frameNum = 0
    sumVal = 0
    preSumVal = 0
    bRecording = False
    bLED = False

    fName = os.path.basename(os.path.splitext(videofile_path)[0])
    fNameExt = os.path.basename(os.path.splitext(videofile_path)[1])

    pathTemp = [os.path.dirname(os.path.splitext(videofile_path)[0]),fName + '_trimmed']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    pathTemp = [savePath,fName + "_trimmed_log.txt"]
    txtPath = os.path.join(*pathTemp)

    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        ret, frame = cap.read()
        frameNum += 1
        if ret == False:
            break
        
        frame_gamma = gammaConv(gamma,frame)

        # LED Detection
        roiFrame = frame_gamma[roiY:roiY+roiH,roiX:roiX+roiW]
        sumVal = roiFrame.T[searchColor].flatten().mean()   
        if sumVal > ledTh: 
            if preSumVal < ledTh:
                bLED = True

        if bLED:
            bRecording = True
            startFrame.append(frameNum)
            pathTemp = [savePath,fName + "_frame_" + str(frameNum) + ".jpg"]
            saveImgPath = os.path.join(*pathTemp)
            cv2.imwrite(saveImgPath,frame_gamma)

        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + ", " + str(sumVal)
        display(cmdText)     

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
    if i == 0:
        checkLEDPos(videoPath[i])
    videoAnalysis(videoPath[i])
