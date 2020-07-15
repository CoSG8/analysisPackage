# coding: UTF-8
# movieTrimming_LED.py
# Akito Kosugi 
# ver.1.1.2    2020.07.15

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
ledTh = 25
trimFrame_pre = 120
trimFrame_post = 240
searchColor = 2
gamma = 1
roiW = 30
roiH = 30

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")


# Define functions
def checkLEDPos(filename,videofile_path,savefile_path):
    interval = 0
    ESC_KEY = 0x1b # Esc キー
    S_KEY = 0x53 # s キー
    R_KEY = 0x52 # r キー
    global frame_1st

    cap = cv2.VideoCapture(videofile_path)
    frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
    ret, frame_1st = cap.read()
    h, w, ch = frame_1st.shape
    
    # window setting
    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", w, h)
    cv2.putText(frame_1st,filename,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st)
    cv2.setMouseCallback("Trimming",get_position)
    cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
    cv2.createTrackbar("Pre","Trimming",trimFrame_pre,360,onTrackbar2)
    cv2.createTrackbar("Post","Trimming",trimFrame_post,360,onTrackbar3)
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
        frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        if frameNum > 1:
            break    

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cap.release()


# Create log file
def create_logFile(filename,savefile_path):
    pathTemp = [savefile_path,filename + "_trimming.log"]
    logPath = os.path.join(*pathTemp)
    f = open(logPath ,'a')
    config = filename +  "\n" + "LED th: " + str(ledTh) + ", Pre frame: " + str(trimFrame_pre) + ", Post frame: " + str(trimFrame_post) + ", LED color: " + str(searchColor) + ", gamma: " + str(gamma) + "\n"
    f.write(config)
    f.close()
    return logPath


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX, roiY
        roiX = x - int(roiW/2)
        roiY = y - int(roiH/2)
        frame_1st_disp  = gammaConv(gamma,frame_1st.copy())
        cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.putText(frame_1st,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.imshow("Trimming",frame_1st_disp)
        display((roiX,roiY))

# Define trackbar
def onTrackbar1(position):
    global ledTh
    ledTh = position
    display("LED Th: " +  str(ledTh))

def onTrackbar2(position):
    global trimFrame_pre
    trimFrame_pre = int(position)
    display("Trimming frame pre: " + str(trimFrame_pre)) 

def onTrackbar3(position):
    global trimFrame_post
    trimFrame_post = int(position)
    display("Trimming frame post: " + str(trimFrame_post)) 

def onTrackbar4(position):
    global searchColor
    searchColor = int(position)
    display("Color: " + str(searchColor)) 

def onTrackbar5(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st.copy())
    cv2.putText(frame_1st,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    display("Gamma : " +  str(gamma))

# Define Gamma conversion
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma


def videoAnalysis(filename,videofile_path,logfile_path,savefile_path):
    startframe = []
    endframe = []
    duration = []
    trialNum = 0
    sumVal = 0
    addFrame = 0
    bLED = False
    bLED_on = False
    bLED_off = False

    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        if ret == False:
            if bLED:
                endframe.append(frameNum)
                duration.append(addFrame)
            break
        frame_gamma = gammaConv(gamma,frame)

        # LED Detection
        roiFrame = frame_gamma[roiY:roiY+roiH,roiX:roiX+roiW]
        if searchColor < 2:
            sumVal = roiFrame.T[searchColor].flatten().mean() - roiFrame.T[2].flatten().mean()
        else:
            sumVal = roiFrame.T[searchColor].flatten().mean() - roiFrame.T[1].flatten().mean()            
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
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + ", Trial: " + str(trialNum) + ", LED value: " + str(sumVal) + ', LED frame: ' + str(addFrame)

        else:
            dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + ", Trial: " + str(trialNum) +  ", LED value: " + str(sumVal)
    
        # Display
        display(dispText)    

    # write log file
    if trialNum > 0:
        for i in range(trialNum):
            f = open(logfile_path ,'a')
            result = "Trial: " + str(i+1) + ", Start frame: " + str(startframe[i]) + ", End frame: " + str(endframe[i]) + ", Duration: " + str(duration[i]) +"\n"
            f.write(result)
        f.close()

    # Display
    dispText = "Number of Trials: " + str(trialNum) + ', Start frame: ' + str(startframe) + ', End frame: ' + str(endframe)
    display(dispText)
    
    cap.release()
    return startframe, endframe, duration, trialNum


def videoTrimming(fileName,videofile_path,savefile_path,startframe,endframe):
    
    trimStartFrame_np = np.array(startframe)
    trimStartFrame_np -= trimFrame_pre
    trimStartFrame = list(trimStartFrame_np)
    trimEndFrame_np = np.array(endframe)
    trimEndFrame_np += trimFrame_post
    trimEndFrame = list(trimEndFrame_np)

    cap = cv2.VideoCapture(videofile_path)
    ret, frame = cap.read()
    h, w, ch = frame.shape

    # Trimming
    for i in range(len(trimStartFrame)):
        if i < 9:
            pathTemp = [savefile_path,fName + "_trial_0" + str(i+1) + ".avi"]
        else:
            pathTemp = [savefile_path,fName + "_trial_" + str(i+1) + ".avi"]
        videoSavePath = os.path.join(*pathTemp)
        dst = cv2.VideoWriter(videoSavePath, fourcc, 30.0, (w,h)) 
        
        cap.set(cv2.CAP_PROP_POS_FRAMES,trimStartFrame[i]-1)
        trimFrameNum = 0

        # Video capture
        while(True):
            frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
            ret,frame = cap.read()
            if frameNum < trimEndFrame[i]:
                frame_gamma = gammaConv(gamma,frame)
                trimFrameNum += 1
                text = fileName + " Start: " + str(trimStartFrame[i]) + " Frame: " + str(trimFrameNum) 
                cv2.putText(frame_gamma,text,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
                dst.write(frame_gamma) 
                # Display
                dispText = "Trial: " + str(i+1)  + ", Frame: " + str(frameNum) + ", Start: " + str(trimStartFrame[i]) + ", Trim: " + str(trimFrameNum)
                display(dispText)    
            else:
                break

    pathTemp = [savePath, 'temp.avi']
    saveName = os.path.join(*pathTemp)
    dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w))
    os.remove(saveName)
    cap.release()


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
videoPath = list(files)

# Analysis
for i in range(len(files)):

    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(videoPath[i])[0]),fName + '_trimming']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)
    
    if i == 0:
        checkLEDPos(fName,videoPath[i],savePath)

    logPath = create_logFile(fName,savePath)

    startFrame, endFrame, duration, trialNum = videoAnalysis(fName,videoPath[i],logPath,savePath)
    if trialNum > 0:
        videoTrimming(fName,videoPath[i],savePath,startFrame,endFrame)
