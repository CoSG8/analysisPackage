# BeamWakling_preProcess
# Progarmmed by Akito Kosugi 
# ver.1.0    2019.03.27 <br>
# ver.1.1    2019.04.08 <br>
# ver.1.2    2019.04.09 <br>
# ver.1.2.1  2019.04.11 <br>
# ver.1.3    2019.04.16 <br>
# ver.1.4    2019.04.17 <br>
# ver.1.4.1  2019.04.25 <br>
# ver.1.4.2  2019.04.26 <br>
# ver.1.4.3  2019.05.10 <br>
# ver.1.4.4  2019.05.13 <br>
# ver.1.4.5  2019.05.14 <br>
# ver.1.4.6  2019.05.21 <br>
# ver.1.4.7  2019.05.22 <br>
# ver.1.4.8  2019.05.24 <br>
# ver.1.4.9  2019.07.22 <br>
# ver.1.4.10 2019.07.24 <br>
# ver.1.4.11 2019.07.26 <br>
# ver.1.5.0  2019.07.29 <br>
# ver.1.5.1  2019.07.30 <br>
# ver.1.6    2019.08.06 <br>
# ver.1.6.1  2019.08.07 <br>
# ver.2.0    2019.09.09 <br>
# ver.2.1    2019.09.18 <br>
# ver.2.2    2019.10.03 <br>
# ver.2.3    2019.10.10 <br>

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display


# Initialization
ESC_KEY = 0x1b # Esc キー
S_KEY = 0x53 # s キー
R_KEY = 0x52 # r キー
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


# Open file
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
videoPath = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)
fName = os.path.basename(os.path.splitext(videoPath)[0])
fNameExt = os.path.basename(os.path.splitext(videoPath)[1])

pathTemp = [os.path.dirname(os.path.splitext(videoPath)[0]),fName + '_trimmed']
savePath = os.path.join(*pathTemp)
os.makedirs(savePath, exist_ok=True)
pathTemp = [savePath,fName + "_trimmed_log.txt"]
txtPath = os.path.join(*pathTemp)

display(videoPath)
display(savePath)


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX, roiY, roiW, roiH
        roiW = 20
        roiH = 20
        roiX = x - int(roiW/2)
        roiY = y - int(roiH/2)
        print((roiX,roiY))
        frame_1st_disp = frame_1st.copy()
        cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(15,241,255),3)
        cv2.imshow("Trimming",frame_1st_disp)


# Define trackBar
def onTrackbar1(position):
    global ledTh
    ledTh = position
    display("LED Th: " +  str(ledTh))


def onTrackbar2(position):
    global frame_pre
    frame_pre = position
    display("pre frame: " +  str(frame_pre))

def onTrackbar3(position):
    global frame_post
    frame_post = position
    display("post frame: " +  str(frame_post))

def onTrackbar4(position):
    global gamma
    global gamma_cvt
    gamma = position / 100
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gamma)
    frame_1st_disp = frame_1st.copy()
    frame_gamma_disp = cv2.LUT(frame_1st_disp, gamma_cvt)
    cv2.imshow("Trimming",frame_gamma_disp)
    display("Gamma: " + str(gamma))

def onTrackbar5(position):
    global searchColor
    global idx
    searchColor = int(position)
    display("Color: " + str(searchColor))


# Run Analysis
ledTh = 150
frame_pre = 30
frame_post = 60
searchColor = 2

cap = cv2.VideoCapture(videoPath)
totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

ret, frame_1st = cap.read()
frameNum += 1
h, w, ch = frame_1st.shape
frame_gamma_1st = cv2.LUT(frame_1st, gamma_cvt)

cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Trimming", w, h)
cv2.imshow("Trimming",frame_1st)
text = fName + ' Frame:' + str(frameNum)
cv2.putText(frame_gamma_1st, text, (20, 40), font, 1, (0,0,255), 2, cv2.LINE_AA)
cv2.setMouseCallback("Trimming",get_position)
cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
cv2.createTrackbar("Pre frame","Trimming",frame_pre,500,onTrackbar2)
cv2.createTrackbar("Post frame","Trimming",frame_post,500,onTrackbar3)
cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar4)
cv2.createTrackbar("Color","Trimming",searchColor,2,onTrackbar5)

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
        
    frame_gamma = cv2.LUT(frame, gamma_cvt)
    
    roiFrame = frame_gamma[roiY:roiY+roiH,roiX:roiX+roiW]
    sumVal = roiFrame.T[searchColor].flatten().mean()

    if sumVal > ledTh: 
        bLED = True
    else:
        if preSumVal > ledTh:
            addFrame = frameNum
        bLED = False

    if bLED:
        if preSumVal < ledTh:
            bRecording = True
            trialNum += 1
            startFrame.append(frameNum) 
            text = fName + " Trial: " + str(trialNum) +" Start: " + str(startFrame[trialNum-1]) + " Frame: " + str(recFrameNum)
            cv2.putText(frame_gamma,text,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
           
            # cv2.imshow("Trimming",frame_gamma)

    if bRecording and bLED == False:
        bRecording = False
        endFrame.append(frameNum)
        duration.append(endFrame[trialNum-1]-startFrame[trialNum-1]);
        f = open(txtPath ,'a')
        # if trialNum == 1:
        #     config = fName + fNameExt + ", gamma: " + str(gamma) + ", pre Frame: " + str(frame_pre) + ", post Frame: " + str(frame_post) + "\n"
        #     f.write(config)
        # f.write(result)
        f.close()
        recFrameNum = 0

    if bRecording:
        recFrameNum = frameNum - startFrame[trialNum-1]
        text1 = fName + " Start: " + str(startFrame[trialNum-1]) + " Frame: " + str(recFrameNum)
        cv2.putText(frame_gamma,text1,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        # cv2.imshow("Trimming",frame_gamma)
        cmdText = "Trial: " + str(trialNum) +" Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Value: " + str(sumVal) + ' Rec frame: ' + str(recFrameNum)

    else:
        text = fName + " Trial: " + str(trialNum) +" Frame: " + str(frameNum) + " / " + str(totalFrameNum) 
        cv2.putText(frame_gamma,text,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.rectangle(frame_gamma,(roiX,roiY),(roiX+roiW,roiY+roiH),(0,0,255),2)
        # cv2.imshow("Trimming",frame_gamma)
        cmdText = "Trial: " + str(trialNum) +" Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Value: " + str(sumVal)

    display(cmdText)
    preSumVal = sumVal

cv2.waitKey(1)    
cv2.destroyAllWindows()
cv2.waitKey(1)

cmdText = 'Start frame: ' + str(startFrame)
display(cmdText)
cmdText = 'Duration: ' + str(duration)
display(cmdText)
display(savePath)


# Run 2nd analysis
bRecording = False
frameNum = 0
recFrame = 0
trialIdx = 0

cap = cv2.VideoCapture(videoPath)
f = open(txtPath ,'a')
config = fName + fNameExt + ", gamma: " + str(gamma) +  ", pre frame: " + str(frame_pre) + ", post frame: " + str(frame_post) + "\n"
f.write(config)
f.close()

while(True):
    
    # Frame capture
    ret, frame = cap.read()
    frameNum += 1

    if ret == False:
        break
    if trialIdx > len(startFrame) - 1:
        break
    
    frame_gamma = cv2.LUT(frame, gamma_cvt)
    
    # Stop recording   
    if bRecording:
        if frameNum > endFrame[trialIdx] + frame_post - 1:
            trialIdx += 1
            f = open(txtPath ,'a')
            result = "Trial: " + str(trialIdx) + " Start frame: " + str(frameNum - recFrame) + ", Rec frame: " + str(recFrame) +  ", Duration: " + str(duration[trialIdx-1]) +"\n"
            f.write(result)
            f.close()       
            dst.release(); 
            bRecording = False
            recFrame = 0
    # Start recording           
    else:
        if frameNum > startFrame[trialIdx] - frame_pre:
            bRecording = True
            pathTemp = [savePath, fName + "_trimmed_trial_" + str(trialIdx+1) + '.avi']
            saveName = os.path.join(*pathTemp)
            dst = cv2.VideoWriter(saveName, fourcc, 30.0, (w,h)) 
    
    if bRecording:
        recFrame += 1
        text = fName + " Start: " + str(startFrame[trialIdx-1]-frame_pre) + " Frame: " + str(recFrame) 
        cv2.putText(frame_gamma,text,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)
        dst.write(frame_gamma)      
        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialIdx+1) + " Rec: " + str(recFrame) 
    else:
        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialIdx)    

    display(cmdText)

cv2.waitKey(1)    
cv2.destroyAllWindows()
cv2.waitKey(1)


pathTemp = [savePath, 'temp.avi']
saveName = os.path.join(*pathTemp)
dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w)) 