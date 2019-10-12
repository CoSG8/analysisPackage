# ### LadderForcePlate_preProcess
# Progarmmed by Akito Kosugi <br>
# ver.1.0   2019.08.13 <br>
# ver.1.0.1 2019.08.15 <br>
# ver.2.0   2019.08.16 <br>
# ver.2.1   2019.08.17 <br>
# ver.2.2   2019.08.18 <br>
# ver.2.3   2019.08.21 <br>
# ver.2.4   2019.08.22 <br>
# ver.2.5   2019.08.26 <br>
# ver.2.6   2019.08.27 <br>
# ver.2.7   2019.08.28 <br>
# ver.2.8   2019.08.30 <br>
# ver.2.8.1 2019.08.30 <br>
# ver.2.9   2019.09.01 <br>
# ver.2.10  2019.09.12 <br>
# ver.2.11  2019.09.25 <br>
# ver.2.12  2019.10.10 <br>
# 
# LadderClimbing_preProcess
# ver.1.1   2019.04.16 <br>
# ver.1.2   2019.04.23 <br>
# ver.1.2.1 2019.04.24 <br>
# ver.1.2.2 2019.05.21 <br>
# ver.1.2.3 2019.05.24 <br>
# ver.1.2.4 2019.06.18 <br>
# 
# BeamWakling_preProcess <br>
# ver.1.0   2019.03.27 <br>
# ver.1.1   2019.04.08 <br>
# ver.1.2   2019.04.09 <br>
# ver.1.2.1 2019.04.11 <br>
# ver.1.3   2019.04.16 <br>


# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

import tkinter
from tkinter import filedialog as tkFileDialog


# Initialization
ESC_KEY = 0x1b # Esc キー
# S_KEY = 0x53 # S キー
# R_KEY = 0x52 # R キー
S_KEY = 0x73 # s キー
R_KEY = 0x72 # r キー
interval = 0
frameNum = 0
recFrameNum = 0
trialNum = 0
sumVal = 0
preSumVal = 0
addFrame = 0
ledTh = 0
x_mean = 0
y_mean = 0
preY_mean = 0
x_array = []
y_array = []
area_array = []
orbit = []
startFrame = []
startFrame_trig = []

bTrig = False
bRecording = False
bLED = False

angle = 90
scale = 1

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

# Gamma conversion
gamma = 100
gamma_cvt = np.zeros((256,1), dtype=np.uint8)
for i in range(256):
    gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / (gamma/100))


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
pathTemp = [savePath,fName + "_trimmed_trajectory.txt"]
txtPath2 = os.path.join(*pathTemp)

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
        frame_gamma_1st_disp = frame_gamma_1st.copy()
        cv2.rectangle(frame_gamma_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
        cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
        cv2.imshow("Trimming",frame_gamma_1st_disp)

# Define trackBar
def onTrackbar1(position):
    global ledTh
    ledTh = position
    display("LED Th: " +  str(ledTh))

def onTrackbar2(position):
    global th_bi
    th_bi = position
    display("Binary Th: " + str(th_bi))

def onTrackbar3(position):
    global heightTh 
    heightTh  = position
    frame_gamma_1st_disp = frame_gamma_1st.copy()
    cv2.rectangle(frame_gamma_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
    cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_gamma_1st_disp, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_gamma_1st_disp)
    display("Height Th : " +  str(heightTh))

def onTrackbar4(position):
    global maskX 
    maskX = position
    frame_gamma_1st_disp = frame_gamma_1st.copy()
    cv2.rectangle(frame_gamma_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
    cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_gamma_1st_disp, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_gamma_1st_disp)
    display("mask X : " +  str(maskX))

def onTrackbar5(position):
    global maskW
    maskW = position
    frame_gamma_1st_disp = frame_gamma_1st.copy()
    cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_gamma_1st_disp, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_gamma_1st_disp)
    display("mask width : " +  str(maskX))

def onTrackbar6(position):
    global gamma
    global gamma_cvt
    gamma = position / 100
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gamma)
    frame_1st_disp = frame_1st_trans.copy()
    frame_gamma_disp = cv2.LUT(frame_1st_disp, gamma_cvt)
    cv2.rectangle(frame_gamma_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_gamma_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_gamma_disp, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_gamma_disp)
    display("Gamma : " +  str(gamma))

def onTrackbar7(position):
    global searchColor
    global idx
    searchColor = int(position)
    if searchColor == 0:
        idx = [0,2]
    elif searchColor == 2:
        idx = [2,0]
    display("Color: " + str(searchColor))    


# Run 1st analysis
ledTh = 170
recInterval = 300
searchColor = 0
th_bi = 90
heightTh = 1000
maskX = 175
maskY = 40
roiW = 0
roiH = 0
roiX = 0
roiY = 0

kernel_open = np.ones((5,5),np.uint8)
kernel_close = np.ones((5,5),np.uint8)

cap = cv2.VideoCapture(videoPath)
totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

ret, frame_1st = cap.read()
frameNum += 1

h, w, ch = frame_1st.shape

maskW = h - maskX*2
maskH = w - maskY

center = (int(w/2), int(h/2))
trans = cv2.getRotationMatrix2D(center, angle , scale)
transpose_img = frame_1st.transpose(1,0,2)
frame_1st_trans = transpose_img[:,::-1]
frame_gamma_1st = cv2.LUT(frame_1st_trans, gamma_cvt)
frame_gamma_1st_disp = frame_gamma_1st.copy()

cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Trimming", h, w)
text = fName
cv2.putText(frame_gamma_1st_disp, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
cv2.imshow("Trimming",frame_gamma_1st_disp)

cv2.setMouseCallback("Trimming",get_position)
cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
cv2.createTrackbar("Binary Th","Trimming",th_bi,255,onTrackbar2)
cv2.createTrackbar("Height Th","Trimming",heightTh,1200,onTrackbar3)
cv2.createTrackbar("Mask X","Trimming",maskX,300,onTrackbar4)
cv2.createTrackbar("Mask W","Trimming",maskW,600,onTrackbar5)
cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar6)
cv2.createTrackbar("Color","Trimming",searchColor,2,onTrackbar7)

while(True):
    
    key = cv2.waitKey(interval)
    if key == ESC_KEY:
        break 
    elif key == R_KEY:
        interval = 0 
    elif key == S_KEY:
        interval = 30

        # Background setting 
        back = np.zeros((w,h,3), dtype=np.uint8)
        mask = cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(255, 255, 255),-1)
        mask_g = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
        frame_1st_mask = frame_gamma_1st.copy()
        frame_1st_mask[mask_g==0] = [0,0,0]
        frame_1st_mask_g = cv2.cvtColor(frame_1st_mask,cv2.COLOR_BGR2GRAY)
        frame_back =  frame_1st_mask_g.astype(np.float32)
     
    # Frame capture
    ret, frame = cap.read()
    frameNum += 1
    if ret == False:
        break

    # Masking 
    transpose_img = frame.transpose(1,0,2)
    frame_trans = transpose_img[:,::-1]
    frame_gamma = cv2.LUT(frame_trans, gamma_cvt)
    frame_mask = frame_gamma.copy()
    frame_mask[mask_g==0] = [0,0,0]
    frame_mask_g = cv2.cvtColor(frame_mask,cv2.COLOR_BGR2GRAY)

    # LED Detection
    if bTrig == False:
        roiFrame = frame_gamma[roiY:roiY+roiH,roiX:roiX+roiW]
        sumVal = roiFrame.T[searchColor].flatten().mean()   
        if sumVal > ledTh: 
            if preSumVal < ledTh:
                bTrig = True
                trigFrame = frameNum
                frame_back =  frame_mask_g.astype(np.float32)
                f = open(txtPath2 ,'a')
                config = fName + fNameExt + ", gamma: " + str(gamma) + ", trig frame: " + str(trigFrame) + "\n" + "Frame from trig, num_of_contours, x_mean, y_mean\n"
                f.write(config)
                f.close()
                pathTemp = [savePath,fName + "_bg.jpg"]
                imgPath = os.path.join(*pathTemp)
                cv2.imwrite(imgPath,frame_gamma)
                cv2.waitKey(1)
                cv2.destroyAllWindows()
                cv2.waitKey(1)

    
    # Differential
    if bTrig:
        frame_diff = cv2.absdiff(frame_mask_g.astype(np.float32),frame_back)
        ret, frame_diff_bi = cv2.threshold(frame_diff, th_bi, 255, cv2.THRESH_BINARY)
        frame_diff_opening = cv2.morphologyEx(frame_diff_bi, cv2.MORPH_OPEN, kernel_open)
        frame_diff_closing = cv2.morphologyEx(frame_diff_opening, cv2.MORPH_CLOSE, kernel_close)
        frame_con, contours, hierarchy = cv2.findContours(frame_diff_closing.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            num_contours = 0
            x_array.append(0)
            y_array.append(0)
            orbit = []
        else:
            num_contours = len(hierarchy[0])
            for cnt in contours:
            # 輪郭に外接する長方形を取得する。
                x, y, width, height = cv2.boundingRect(cnt)
                x_array.append(x+width/2)
                y_array.append(y+height/2)
                area_array.append(width*height)
                # cv2.rectangle(frame_mask,(x, y),(x + width, y + height),(0, 255, 0),1)    

        # Moving frame detection
        if num_contours > 5:
            weight = []
            for val in area_array:
                weight.append(val/sum(area_array))
            x_mean = np.average(x_array, weights = weight)
            y_mean = np.average(y_array, weights = weight)
        else:
            x_mean = 0
            y_mean = 0
        center = (int(x_mean), int(y_mean))
        orbit.append(center)
        f = open(txtPath2 ,'a')
        result = str(frameNum-trigFrame) + ", " + str(num_contours) + ", " + str(x_mean) + ", " + str(y_mean)   + ",\n"
        f.write(result)
        f.close()

        if bRecording == False:
            if preY_mean  > heightTh:
                if y_mean  < heightTh: 
                    if y_mean  > 0:
                        trialNum += 1
                        bRecording = True
                        startFrame.append(frameNum)
                        startFrame_trig.append(frameNum - trigFrame)
                        addFrame = 0
        
    # Recording
    if bRecording:       
        addFrame += 1
        text = fName + " Start: " + str(startFrame[trialNum-1]) + " Frame: " + str(addFrame) 
        cv2.putText(frame_gamma,text,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)

        if addFrame > recInterval:
            bRecording = False
        
    # Display
    if bTrig:       
        frame_diff_g = cv2.cvtColor(frame_diff_closing,cv2.COLOR_GRAY2BGR)
        if bRecording:
            text = fName + " Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trig: " + str(trigFrame)  + " Rec: " + str(addFrame)
            cv2.putText(frame_diff_g,text,(10,20),font,0.7,(0,0,255),2,cv2.LINE_AA)     
            cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialNum) + " Contours: " + str(num_contours)  + ' Y: ' + str(y_mean)  + " Rec: " + str(addFrame)
        else:
            text = fName + " Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trig: " + str(trigFrame)
            cv2.putText(frame_diff_g,text,(10,20),font,0.7,(0,0,255),2,cv2.LINE_AA)     
            cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialNum) + " Contours: " + str(num_contours)  + ' Y: ' + str(y_mean)
        frame_contour = cv2.drawContours(frame_diff_g,contours, -1, (0,0,255), 1)  
        if  num_contours > 0:
            for i in orbit:
                cv2.circle(frame_diff_g,i,3,(0,255,0),-1)
            cv2.circle(frame_diff_g,center,10,(0,255,0),-1)
        cv2.rectangle(frame_diff_g,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
        cv2.line(frame_diff_g,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
        # cv2.imshow("Trimming",frame_diff_g.astype(np.uint8))
    else:
        text = fName + " Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Value: " + str(sumVal)
        cv2.putText(frame_gamma,text,(10,20),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.rectangle(frame_gamma,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.imshow("Trimming",frame_gamma)
        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Value: " + str(sumVal)
    
    display(cmdText)

    x_array = []
    y_array = []
    area_array = []
    preSumVal = sumVal
    preY_mean = y_mean  

cv2.waitKey(1)    
cv2.destroyAllWindows()
cv2.waitKey(1)

cmdText = 'Start frame: ' + str(startFrame)

display(cmdText)
display(savePath)

back = np.zeros((w,h,3), dtype=np.uint8)
for i in orbit:
    cv2.circle(back,i,3,(0,255,0),-1)
cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
pathTemp = [savePath,fName + "_trajectory.jpg"]
imgPath = os.path.join(*pathTemp)
cv2.imwrite(imgPath,back.astype(np.uint8))


# Run 2nd analysis

frame_pre = 60
frame_post = 300
frameNum = 0
addFrame = 0
trialIdx = 0
bRecording = False

cap = cv2.VideoCapture(videoPath)
totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

f = open(txtPath ,'a')
config = fName + fNameExt + ", gamma: " + str(gamma) + ", trig frame: " + str(trigFrame) + ", pre frame: " + str(frame_pre) + ", post frame: " + str(frame_post) + "\n"
f.write(config)
f.close()
                                
while(True):
    
    # Frame capture
    ret, frame = cap.read()
    frameNum += 1
    frameNum_trig = frameNum - trigFrame
    if ret == False:
        break
    if trialIdx > len(startFrame) - 1:
        break
    
    transpose_img = frame.transpose(1,0,2)
    frame_trans = transpose_img[:,::-1]
    frame_gamma = cv2.LUT(frame_trans, gamma_cvt)
    
    # Stop recording   
    if bRecording:
        if addFrame > frame_pre + frame_post - 2:
            trialIdx += 1
            f = open(txtPath ,'a')
            result = "Trial: " + str(trialIdx) + ", Moving frame: " + str(startFrame_trig[trialIdx-1]) + " Start, frame: " + str(startFrame_trig_pre) + ", Rec frame: " + str(addFrame+1) + "\n"
            f.write(result)
            f.close()        
            bRecording = False
            addFrame = 0
    # Start recording           
    else:
        if frameNum > startFrame[trialIdx] - frame_pre:
            bRecording = True
            startFrame_trig_pre = frameNum_trig
            pathTemp = [savePath, fName + "_trimmed_trial_" + str(trialIdx+1) + '.avi']
            saveName = os.path.join(*pathTemp)
            dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w)) 
    
    if bRecording:
        addFrame += 1
        text = fName + " Start: " + str(startFrame_trig_pre) + " Frame: " + str(addFrame) 
        cv2.putText(frame_gamma,text,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)
        dst.write(frame_gamma)      
        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialIdx+1) + " Rec: " + str(addFrame) 
    else:
        cmdText = "Frame: " + str(frameNum) + " / " + str(totalFrameNum) + " Trial: " + str(trialIdx)    

    display(cmdText)

cv2.waitKey(1)    
cv2.destroyAllWindows()
cv2.waitKey(1)


pathTemp = [savePath, 'temp.avi']
saveName = os.path.join(*pathTemp)
dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w)) 