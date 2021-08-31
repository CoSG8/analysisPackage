# coding: UTF-8
# frameSelection_Calib.py
# Akito Kosugi 
# ver.1.1    2021.08.31

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display
from utils import frameselectiontools

# Initialization
ledTh = 30
searchColor = 2
roiW = 30
roiH = 30

start = 0
stop = 0.9
numframes2pick = 300
crop = False
coords = [0,1280,0,720]
cluster_step = 1
cluster_resizewidth = 30
cluster_color = False

roiX_array = []
roiY_array = []
color_array = []
ledTh_array = []

savePath = []
logPath = []
ledFrame = []

font = cv2.FONT_HERSHEY_SIMPLEX


# Define functions
def checkLEDPos(filename,videofile_path):
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
    cv2.namedWindow("Selection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Selection", w, h)
    cv2.putText(frame_1st,filename,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Selection",frame_1st)
    cv2.setMouseCallback("Selection",get_position)
    cv2.createTrackbar("LED th","Selection",ledTh,255,onTrackbar1)
    cv2.createTrackbar("Color","Selection",searchColor,2,onTrackbar2)

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


def LED_detection(videofile_path,logfile_path,roix,roiy,ledth,searchcolor):
    sumVal = 0

    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        if ret == False:
            break

        # LED Detection
        roiFrame = frame[roiy:roiy+roiH,roix:roix+roiW]
        if searchcolor < 2:
            sumVal = roiFrame.T[searchcolor].flatten().mean() - roiFrame.T[2].flatten().mean()
        else:
            sumVal = roiFrame.T[searchcolor].flatten().mean() - roiFrame.T[1].flatten().mean()            
        if sumVal > ledth:
            ledFrame = frameNum
            break

        # Display
        dispText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) +  ", LED value: " + str(sumVal)   
        display(dispText)    

    # write log file
    f = open(logfile_path ,'a')
    result = "LED frame: " + str(ledFrame) + "\n"
    f.write(result)
    f.close()

    # Display
    dispText = 'LEd frame: ' + str(ledFrame)
    display(dispText)
    
    cap.release()
    return ledFrame


# Create log file
def create_logFile(filename,savefile_path,ledth,searchcolor):
    pathTemp = [savefile_path,filename + "_selection.log"]
    logPath = os.path.join(*pathTemp)
    f = open(logPath ,'a')
    config = filename +  "\n" + "LED th: " + str(ledth) + " LED color: " + str(searchcolor) + "\n"
    f.write(config)
    f.close()
    return logPath


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX, roiY
        roiX = x - int(roiW/2)
        roiY = y - int(roiH/2)
        frame_1st_disp  = frame_1st.copy()
        cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.putText(frame_1st,fName,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.imshow("Selection",frame_1st_disp)
        display((roiX,roiY))


# Define trackbar
def onTrackbar1(position):
    global ledTh
    ledTh = position
    display("LED Th: " +  str(ledTh))


def onTrackbar2(position):
    global searchColor
    searchColor = int(position)
    display("Color: " + str(searchColor)) 


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

pathTemp = [os.path.dirname(videoPath[0]),'calibration_images_all']
path_images = os.path.join(*pathTemp)
os.makedirs(path_images, exist_ok=True)

# Check led and create save directory
for i in range(len(files)):
    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])

    checkLEDPos(fName,videoPath[i])
    roiX_array.append(roiX)
    roiY_array.append(roiY)
    ledTh_array.append(ledTh)
    color_array.append(searchColor)

    logPath.append(create_logFile(fName,path_images,ledTh_array[i],color_array[i]))


# LED detection
for i in range(len(files)):
    ledFrame.append(LED_detection(videoPath[i],logPath[i],roiX_array[i],roiY_array[i],ledTh_array[i],color_array[i]))	

# k means clustering
cap = cv2.VideoCapture(videoPath[0])
ret, frame = cap.read()
h, w, ch = frame.shape
coords = [0,w,0,h]
totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
start = float(ledFrame[0]/totalFrameNum)
frames2pick = frameselectiontools.KmeansbasedFrameselectioncv2(cap,numframes2pick-1,start,stop,crop,coords,step=cluster_step,resizewidth=cluster_resizewidth,color=cluster_color)
frames2pick_np = np.array(frames2pick)
frames2pick_np -= ledFrame[0]
cap.release()

# Selection frames
for i in range(len(files)):

	cap = cv2.VideoCapture(videoPath[i])
	selectFrame = list(frames2pick_np+ledFrame[i])
	f = open(logPath[i],'a')
	result = "Selection frames: " + str(selectFrame) + "\n"
	f.write(result)
	f.close()
	display("Selection frames:" + str(selectFrame))

	k = 0
	for j in selectFrame:
		k += 1
		cap.set(cv2.CAP_PROP_POS_FRAMES,j-1)
		ret,frame = cap.read()
		cv2.putText(frame,str(j),(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
		if k < 10:
			saveName = "camera-" + str(i+1) + "-0" + str(k)
		else:
			saveName = "camera-" + str(i+1) + "-" + str(k)
		pathTemp = [path_images,saveName+".jpg"]
		imgSavePath = os.path.join(*pathTemp)
		cv2.imwrite(imgSavePath,frame)
