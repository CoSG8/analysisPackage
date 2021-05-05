# coding: UTF-8
# movieTracking_camShift.py
# Progarmmed by Akito Kosugi
# ver.1.1.1 2020.12.30

# Import
import cv2
import math
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
ESC_KEY = 0x1b # Esc キー
S_KEY = ord('s')
R_KEY = ord('r')
interval = 30
orbit = []
frameNum = 0
w_ini = 30
h_ini = 30
bAnalysis = False

threshold = 170
gamma = 1
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

font = cv2.FONT_HERSHEY_SIMPLEX
cri = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 10, 1)


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:    
        global rct
        rct = (x, y, w_ini, h_ini)  
        print(rct)
        frame_1st_disp  = gammaConv(gamma,frame.copy())
        cv2.circle(frame_1st_disp,(x,y),7,(15,241,255),3)
        cv2.imshow("Tracking",frame_1st_disp )

# Define trackBar
def onTrackbar(position):
    global threshold
    threshold = position
    display("threshold: " + str(threshold))

def onTrackbar2(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st.copy())
    #cv2.putText(frame_1st,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("Tracking",frame_1st_disp)
    display("Gamma : " +  str(gamma))

# Define Gamma conversion
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma


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

# Analysis
for i in range(len(files)):

    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(videoPath[i])[0]),fName + '_tracking']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)
    

# Run Analysis
cap = cv2.VideoCapture(videoPath[0])
ret, frame_1st = cap.read()
freme = frame_1st.copy()
frameNum += 1
h, w, ch = frame_1st.shape
pathTemp = [savePath,fName+'_tracking.avi']
saveName = os.path.join(*pathTemp)
dst = cv2.VideoWriter(saveName , fourcc, 30.0, (w,h))

cv2.namedWindow("Tracking", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Tracking", w, h)
cv2.startWindowThread()
cv2.imshow("Tracking",frame_1st)
text =  fName + ' Frame:' + str(frameNum)
#cv2.putText(frame_1st, text, (10, 30), font, 1, (0,0,255), 3, cv2.LINE_AA)
cv2.setMouseCallback("Tracking",get_position)
cv2.createTrackbar("Threshold","Tracking",threshold,255,onTrackbar)
#cv2.createTrackbar("Gamma","Tracking",gamma,300,onTrackbar2)

while(True):
    if frameNum == 1:
        interval = 0
        pathTemp = [savePath,fName + "_tracking.csv"]
        dataPath = os.path.join(*pathTemp)
        f = open(dataPath ,'a')
        result = "Frame, x, y, \n"
        f.write(result)
    
    ret, frame = cap.read()
    frameNum += 1
    if ret == False:
        break
    
    key = cv2.waitKey(interval)
    if key == ESC_KEY:
        break 
    elif key == R_KEY:
        bAnalysis = False
    elif key == S_KEY:
        bAnalysis = True
    if(bAnalysis):
        interval = 30
    else:
        interval = 0

    # Gamma conversion
    frame_write = frame.copy()
    frame_b,frame_g,frame_r = cv2.split(frame_write)
    
    if(bAnalysis):        
    	# img_g = cv2.cvtColor(frame_gamma, cv2.COLOR_BGR2GRAY)
        img_g = frame_r.copy()
        ret, img_bin = cv2.threshold(img_g, threshold, 255, cv2.THRESH_BINARY)    
        ret, rct = cv2.CamShift(img_bin, rct, cri)
        x, y, w, h = rct
        center = (int(x)+math.floor(w/2), int(y)+math.floor(h/2))
        orbit.append(center)
        for i in orbit:
            cv2.circle(frame_write,i,3,(255,0,0),3)
        result = str(frameNum) + ", " + str(center[0]) + ", " + str(center[1]) + "," 
        f.write(result + "\n")
        display(result)

    text = fName + ' Frame:' + str(frameNum)
    #cv2.putText(frame_gamma, text, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    
    cv2.imshow("Tracking",frame_write)
    #cv2.imshow("Tracking",img_g)
    #cv2.imshow("Tracking",img_bin)
    dst.write(frame_write)
    
f.close()

pathTemp = [savePath,fName + "_trajectory.jpg"]
imgPath = os.path.join(*pathTemp)
cv2.imwrite(imgPath,frame_write)

cv2.waitKey(1)    
cv2.destroyAllWindows()
cv2.waitKey(1)

pathTemp = [savePath, 'temp.avi']
saveName = os.path.join(*pathTemp)
dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w))
#os.remove(saveName)
cap.release()
