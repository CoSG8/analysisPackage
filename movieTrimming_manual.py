# coding: UTF-8
# movieTrimming_manual.py
# Akito Kosugi 
# ver.1.0.4   2020.07.07

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
font = cv2.FONT_HERSHEY_SIMPLEX
ESC_KEY = 27 # Esc キー
space_key = 32   # Space
enter_key = 13   # Enter
s_KEY = ord('s')
r_KEY = ord('r')
a_KEY = ord('a')

rotAngle = 0
gamma = 1

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

# Define function
# Gamma conversion
def onTrackbar1(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(frame_1st.copy())
    cv2.imshow("Trimming",frame_1st_disp)
    cv2.putText(frame_1st,fName,(10,20),font,0.5,(0,0,255),2,cv2.LINE_AA)
    display("Gamma : " +  str(gamma))

def onTrackbar2(position):
    global rotAngle
    rotAngle = position
    frame_1st_disp = gammaConv(frame_1st.copy())
    cv2.imshow("Trimming",frame_1st_disp)
    cv2.putText(frame_1st,fName,(10,20),font,0.5,(0,0,255),2,cv2.LINE_AA)
    display("Rotation : " +  str(rotAngle))

def gammaConv(img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gamma)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma

# Create log file
def create_logFile(filename,savefile_path):
    pathTemp = [savefile_path,filename + "_trimming.log"]
    logPath = os.path.join(*pathTemp)
    f = open(logPath ,'a')
    config = filename +  "\n" +  "rotation: " + str(rotAngle) + ", gamma: " + str(gamma) + "\n"
    f.write(config)
    f.close()
    return logPath

def frameDisp(frame,numFrame,totalNumFrame,bRecording):
    msg = "s key: play or stop, r key: trim start or stop"
    cv2.putText(frame, msg, (10, 20), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    msg = "enter key: previous frame, space key: previous frame"
    cv2.putText(frame, msg, (10, 40), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    msg = "Frame: " + str(int(numFrame)) + " / " + str(int(totalNumFrame))
    cv2.putText(frame, msg, (30, 70), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    if(bRecording):
        cv2.circle(frame,(15,65),10,(0,0,255),thickness=-1)
    cv2.imshow("img",frame)

def framePreProcessing(frame,rot_angle):
    # Rotation
    if rot_angle == 270:
        frame_rot = cv2.rotate(frame,cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rot_angle == 90:
        frame_rot= cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
    else:
        frame_rot = frame.copy()
    # Gamma conv
    frame_gamma = gammaConv(frame_rot)
    return frame_gamma

def checkFirstFrame(filename,videofile_path):
    global frame_1st
    interval = 0

    cap = cv2.VideoCapture(videofile_path)
    framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
    ret, frame_1st = cap.read()
    h, w, ch = frame_1st.shape
    frame_1st_disp = framePreProcessing(frame_1st,rotAngle)
    
    # window setting
    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", h, w)
    cv2.putText(frame_1st_disp,filename,(10,20),font,0.5,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar1)
    cv2.createTrackbar("Rotation","Trimming",rotAngle,360,onTrackbar2)

    while(True):

        key = cv2.waitKey(interval)
        if key == ESC_KEY:
            break 
        elif key == enter_key:
            interval = 30 
        
        # Frame capture
        framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        if framenum > 1:
            break    

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cap.release()

# Playing and annotation
def movieAnnotation(fileName,videofile_path):
    interval = 0
    startframe = []
    endframe = []
    bRecording = False
    bPlaying = False
    bPlaying_fast = False

    cap = cv2.VideoCapture(videofile_path)
    totalNumFrame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    ret, frame_1st = cap.read()
    numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    frame_1st_gamma = framePreProcessing(frame_1st,rotAngle)
    
    h, w, ch = frame_1st_gamma.shape
    cv2.namedWindow("img", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img", w,h)
    frameDisp(frame_1st_gamma,numFrame,totalNumFrame,bRecording)

    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        frame_gamma = framePreProcessing(frame,rotAngle) 
        frameDisp(frame_gamma,numFrame,totalNumFrame,bRecording)

        if(bPlaying):
            if(bPlaying_fast):
                interval = 3
            else:
                interval = 30
        else:
            if(bPlaying_fast):
                bPlaying_fast = False
                display("Fast-forward stop")
            interval = 0
        key = cv2.waitKey(interval)
        if key == ESC_KEY:
            break 
        elif key == s_KEY:
            bPlaying = not(bPlaying)
        elif key == a_KEY:
            bPlaying_fast = not(bPlaying_fast)
            if(bPlaying_fast):
                display("Fast-forward start")
            else:
                display("Fast-forward stop")
        elif key == r_KEY:
            bRecording = not(bRecording)
            if(bRecording):
                startframe.append(numFrame)
                display("Trim " + str(len(startframe)) + " start: " + str(int(numFrame)) + " frame")
            else:
                endframe.append(numFrame)
                display("Trim " + str(len(startframe)) + " stop: " + str(int(numFrame)) + " frame")
            setFrame = numFrame-2
            cap.set(cv2.CAP_PROP_POS_FRAMES,setFrame)
            ret, frame = cap.read()
            numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            frame_gamma = framePreProcessing(frame,rotAngle)
            frameDisp(frame_gamma,numFrame,totalNumFrame,bRecording)
        elif key == space_key:
            setFrame = numFrame-3
            cap.set(cv2.CAP_PROP_POS_FRAMES,setFrame)
            ret, frame = cap.read()
            numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            frame_gamma = framePreProcessing(frame,rotAngle)
            frameDisp(frame_gamma,numFrame,totalNumFrame,bRecording)

    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cap.release()
    
    # Display
    trialnum = len(startframe)
    dispText = "Number of Trials: " + str(trialnum) + ', Start frame: ' + str(startframe)
    
    return startframe, endframe, trialnum

# Trimming
def videoTrimming(fileName,videofile_path,savefile_path,logfile_path,trimframe_start,trimframe_end):

    cap = cv2.VideoCapture(videofile_path)
    ret, frame = cap.read()
    frame_gamma = framePreProcessing(frame,rotAngle)
    h, w, ch = frame_gamma.shape

    # Trimming
    for i in range(len(trimframe_start)):
        if i < 9:
            pathTemp = [savefile_path,fName + "_trial_0" + str(i+1) + ".avi"]
        else:
            pathTemp = [savefile_path,fName + "_trial_" + str(i+1) + ".avi"]
        videoSavePath = os.path.join(*pathTemp)
        dst = cv2.VideoWriter(videoSavePath, fourcc, 30.0, (w,h)) 
        
        cap.set(cv2.CAP_PROP_POS_FRAMES,trimframe_start[i]-1)
        trimFrameNum = 0

        # Video capture
        while(True):
            framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
            ret,frame = cap.read()
            if framenum < trimframe_end[i]:
                frame_gamma = framePreProcessing(frame,rotAngle)
                trimFrameNum += 1
                text = fileName + " Start: " + str(int(trimframe_start[i])) + " Frame: " + str(trimFrameNum) 
                cv2.putText(frame_gamma,text,(10,20),font,0.5,(0,0,255),2,cv2.LINE_AA)
                dst.write(frame_gamma) 
                # Display
                dispText = "Trial: " + str(i+1)  + ", Frame: " + str(framenum) + ", Start: " + str(int(trimframe_start[i])) + ", Trim: " + str(trimFrameNum)
                display(dispText)    
            else:
                break
        f = open(logfile_path ,'a')
        config = "Trial: " + str(i+1) +  ", Start frame: " + str(int(trimframe_start[i])) + ", recFrame: " + str(trimFrameNum) + "\n"
        f.write(config)
        f.close()

    pathTemp = [savePath, 'temp.avi']
    saveName = os.path.join(*pathTemp)
    dst = cv2.VideoWriter(saveName, fourcc, 30.0, (w,h))
    # os.remove(saveName)
    cap.release()


# Main
# Open file
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
# for Win
# files = tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir)
# for Mac
files = tkinter.filedialog.askopenfilenames(initialdir = iDir)
videoPath = list(files)

# Analyisis
for i in range(len(files)):
    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(videoPath[i])[0]),fName + '_trimming']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)
    
    if i == 0:
        checkFirstFrame(fName,videoPath[i])
        
    logPath = create_logFile(fName,savePath)

    startFrame, endFrame, trialNum = movieAnnotation(fName,videoPath[i])
    videoTrimming(fName,videoPath[i],savePath,logPath,startFrame,endFrame)