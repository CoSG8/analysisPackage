# filesProcessingExample
# Progarmmed by Akito Kosugi 
# ver.1.0    2019.10.12 

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
ledTh = 150
recFrame_pre = 10
recFrame_post = 0
searchColor = 1
gamma = 1

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")


# Define functions
def checkLEDPos(capture,filename,savefile_path):
    frameNum = 0
    interval = 0
    ESC_KEY = 0x1b # Esc キー
    S_KEY = 0x53 # s キー
    R_KEY = 0x52 # r キー
    global frame_1st

    ret, frame_1st = capture.read()
    frameNum += 1
    h, w, ch = frame_1st.shape
    
    # window setting
    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", w, h)
    cv2.imshow("Trimming",frame_1st)
    cv2.setMouseCallback("Trimming",get_position)
    cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
    cv2.createTrackbar("Pre","Trimming",recFrame_pre,240,onTrackbar2)
    cv2.createTrackbar("Post","Trimming",recFrame_post,240,onTrackbar3)
    cv2.createTrackbar("Color","Trimming",searchColor,2,onTrackbar4)
    cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar5)

    while(True):

        key = cv2.waitKey(interval)
        if key == ESC_KEY:
            break 
        elif key == R_KEY:
            interval = 0 
        elif key == S_KEY:
            interval = 30
        if key == S_KEY:
            interval = 30
        
        # Frame capture
        ret, frame = cap.read()
        frameNum += 1
        if frameNum > 1:
            break    

    # write txt file
    pathTemp = [savefile_path,filename + "_trimmed_log.txt"]
    txtPath = os.path.join(*pathTemp)
    f = open(txtPath ,'a')
    config = filename +  "\n" + "LED th: " + str(ledTh) + ", Pre frame: " + str(recFrame_pre) + ", Post frame: " + str(recFrame_post) + ", LED color: " + str(searchColor) + ", gamma: " + str(gamma) + "\n"
    f.write(config)
    f.close()

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
    global recFrame_pre
    recFrame_pre = int(position)
    display("Rec frame pre: " + str(recFrame_pre)) 

def onTrackbar3(position):
    global recFrame_post
    recFrame_post = int(position)
    display("Rec frame post: " + str(recFrame_post)) 

def onTrackbar4(position):
    global searchColor
    searchColor = int(position)
    display("Color: " + str(searchColor)) 

def onTrackbar5(position):
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


def videoAnalysis(capture,filename,savefile_path):
    startframe = []
    endframe = []
    duration = []
    frameNum = 0
    trialNum = 0
    sumVal = 0
    addFrame = 0
    bLED = False
    bLED_on = False
    bLED_off = False

    totalFrameNum = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        ret, frame = capture.read()
        if ret == False:
            if bLED:
                endframe.append(frameNum)
                duration.append(addFrame)
            break
        frameNum += 1        
        frame_gamma = gammaConv(gamma,frame)

        # LED Detection
        roiFrame = frame_gamma[roiY:roiY+roiH,roiX:roiX+roiW]
        sumVal = roiFrame.T[searchColor].flatten().mean()   
        if sumVal > ledTh:
            if bLED == False:
                bLED_on = True
            bLED = True
        else:
            if bLED:
                bLED_off = True
            bLED = False

        if bLED_on:
            trialNum += 1
            startframe.append(frameNum)
            bLED_on = False

        if bLED_off:
            endframe.append(frameNum)
            duration.append(addFrame)
            addFrame = 0
            bLED_off = False

        if bLED:
            addFrame = frameNum - startframe[trialNum-1] + 1
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialNum) + " LED value: " + str(sumVal) + ' LED frame: ' + str(addFrame)
        else:
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialNum) +  " LED value: " + str(sumVal)
    
        # Display
        display(dispText)    

    # write txt file
    pathTemp = [savefile_path,filename + "_trimmed_log.txt"]
    txtPath = os.path.join(*pathTemp)
    for i in range(trialNum):
        f = open(txtPath ,'a')
        result = "Trial: " + str(i) + ", Start frame: " + str(startframe[i]) + ", End frame: " + str(endframe[i]) + ", Duration: " + str(duration[i]) +"\n"
        f.write(result)
    f.close()

    # Display
    dispText = "Number of Trials: " + str(trialNum) ', Start frame: ' + str(startframe)
    display(dispText)
    
    capture.release()
    return startframe, endframe, duration, trialNum


def videoTrimming(capture,fileName,savefile_path,startframe,endframe):
    frameNum = 0
    trialNum = 0
    recFrame = 0
    bRecStart = False
    bRecording = False

    totalFrameNum = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        ret, frame = capture.read()
        if ret == False:
            break
        frameNum += 1
        h, w, ch = frame.shape
        frame_gamma = gammaConv(gamma,frame)

        # Trimming  
        if frameNum > startframe[trialNum]-1 - recFrame_pre:
            if bRecording == False: 
                bRecStart = True
                bRecording = True
        if frameNum > endframe[trialNum] - recFrame_post: 
            if bRecording:
                trialNum += 1
                bRecording = False

        # Recording
        if bRecStart:
            pathTemp = [savefile_path,fName + "_trial_" + str(trialNum+1) + ".avi"]
            videoSavePath = os.path.join(*pathTemp)
            dst = cv2.VideoWriter(videoSavePath, fourcc, 30.0, (w,h)) 
            bRecStart = False
        if bRecording:
            recFrame += 1
            dst.write(frame_gamma) 
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + ",  Trial: " + str(trialNum+1) + " Rec"
        else:
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + ",  Trial: " + str(trialNum)
        
        # Display
        display(dispText)    

    pathTemp = [savePath, 'temp.avi']
    saveName = os.path.join(*pathTemp)
    dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w)) 



# Open files
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
# for Win
# files = tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir)
# for Mac
files = tkinter.filedialog.askopenfilenames(initialdir = iDir)
videoPath = list(files)

# Analysis
for i in range(len(files)):

    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(videoPath[i])[0]),fName + '_trimmed']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)
    
    cap = cv2.VideoCapture(videoPath[i])
    if i == 0:
        cap = cv2.VideoCapture(videoPath[i])
        checkLEDPos(cap,fName,savePath)
    
    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    cap = cv2.VideoCapture(videoPath[i])
    startFrame, endFrame, duration, trialNum = videoAnalysis(cap,fName,savePath)
    if trialNum > 0:
        cap = cv2.VideoCapture(videoPath[i])
        videoTrimming(cap,fName,savePath,startFrame,endFrame)