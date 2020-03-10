# movieTrimming_frame
# Programmed by Akito Kosugi 
# ver.1.0    2020.03.01

# Import
import cv2
import sys
import os
import sys
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
argv = sys.argv
trigFrame = int(argv[1])
trimStartFrame = int(argv[2])
trimFrameNum = int(argv[3])
rotAngle = int(argv[4])

gamma = 1
font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

# Define function
def onTrackbar(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st.copy())
    cv2.imshow("Trimming",frame_1st_disp)
    cv2.putText(frame_1st,fName,(10,20),font,0.7,(0,0,255),2,cv2.LINE_AA)
    display("Gamma : " +  str(gamma))
    
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma


# Open files
root = tkinter.Tk()
root.withdraw()
fTyp = [("","*")]
iDir = os.path.abspath(os.path.dirname('__file__'))
# for Win
files = tkinter.filedialog.askopenfilenames(filetypes = fTyp,initialdir = iDir)
# for Mac
# files = tkinter.filedialog.askopenfilenames(initialdir = iDir)
filePath = list(files)

for i in range(len(filePath)):
    fName = os.path.basename(os.path.splitext(filePath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(filePath[i])[1])
    videofile_path = filePath[i]
    cap = cv2.VideoCapture(videofile_path)
    ret, frame_1st = cap.read()
    # Rotation
    if rotAngle == 270:
        frame_1st = cv2.rotate(frame_1st, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rotAngle == 90:
        frame_1st = cv2.rotate(frame_1st, cv2.ROTATE_90_CLOCKWISE)
    
    h, w, ch = frame_1st.shape    
    
    pathTemp = [os.path.dirname(os.path.splitext(filePath[i])[0]),fName + '_trimming']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)

    pathTemp = [savePath,fName + "_trimming.avi"]
    videosave_path = os.path.join(*pathTemp)   
    dst = cv2.VideoWriter(videosave_path, fourcc, 30.0, (w,h)) 


# Show first frame
interval = 0
ESC_KEY = 0x1b # Esc キー
S_KEY = 0x53 # s キー
R_KEY = 0x52 # r キー


# Window setting
cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Trimming", w, h)
cv2.imshow("Trimming",frame_1st)
cv2.putText(frame_1st,fName,(10,50),font,0.7,(0,0,255),2,cv2.LINE_AA)
cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar)

while(True):
    key = cv2.waitKey(interval)
    if key == ESC_KEY:
        break 
    elif key == S_KEY:
        interval = 0 

    # Frame capture
    frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
    ret, frame = cap.read()
    if frameNum > 1:
        break            
        
cv2.destroyAllWindows()
cv2.waitKey(1)
cap.release()


# Trimming
trimEndFrame = trigFrame + trimStartFrame + trimFrameNum
trimFrame = 0

cap = cv2.VideoCapture(videofile_path)
cap.set(cv2.CAP_PROP_POS_FRAMES,trigFrame + trimStartFrame)

while(True):
    frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
    ret, frame = cap.read()
    if frameNum < trimEndFrame:
    	frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    	frame_gamma = gammaConv(gamma,frame)
    	trimFrame += 1
    	text = fName + " Trig: " + str(trigFrame) +  " Start: " + str(trimStartFrame) + " Frame: " + str(trimFrame) 
    	cv2.putText(frame_gamma,text,(10,20),font,0.7,(0,0,255),2,cv2.LINE_AA)
    	dst.write(frame_gamma)
    	# Display
    	dispText = "Start: " + str(trigFrame + trimStartFrame) + ", Frame: " + str(trimFrame)
    	display(dispText)
    else:
    	break

pathTemp = [savePath, 'temp.avi']
saveName = os.path.join(*pathTemp)
dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w))
# os.remove(saveName)
cap.release()