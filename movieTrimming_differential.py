# coding: UTF-8
# movieTrimming_differential.py
# Akito Kosugi 
# ver.1.0 .1  2020.05.01

# Import
import cv2
import sys
import os
import tkinter
import tkinter.filedialog
import numpy as np
from IPython.core.display import display

# Initialization
ledTh = 20
th_bi = 90
heightTh = 1075
maskX = 175
maskY = 40
trimFrame_pre = 80
trimFrame_post = 400
searchColor = 1
gamma = 1
roiX = 0
roiY = 0
roiW = 0
roiH = 0

ESC_KEY = 0x1b # Esc キー
S_KEY = 0x53 # s キー
R_KEY = 0x52 # r キー
enter_key = 13   # Enter

angle = 90
scale = 1

font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

# Define functions
def checkLEDPos(filename,videofile_path):
    interval = 0
    global frame_1st_trans, maskW, maskH, trans

    cap = cv2.VideoCapture(videofile_path)
    framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
    ret, frame_1st = cap.read()
    h, w, ch = frame_1st.shape

    maskW = h - maskX*2
    maskH = w - maskY

    center = (int(w/2), int(h/2))
    trans = cv2.getRotationMatrix2D(center, angle , scale)
    transpose_img = frame_1st.transpose(1,0,2)
    frame_1st_trans = transpose_img[:,::-1]
    frame_gamma_1st_disp  = gammaConv(gamma,frame_1st_trans.copy())

    # window setting
    cv2.namedWindow("Trimming", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Trimming", h, w)
    cv2.putText(frame_gamma_1st_disp,filename,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.rectangle(frame_gamma_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_gamma_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.imshow("Trimming",frame_gamma_1st_disp)
    cv2.setMouseCallback("Trimming",get_position)
    cv2.createTrackbar("LED th","Trimming",ledTh,255,onTrackbar1)
    cv2.createTrackbar("Binary Th","Trimming",th_bi,255,onTrackbar2)
    cv2.createTrackbar("Height Th","Trimming",heightTh,w,onTrackbar3)
    cv2.createTrackbar("Mask X","Trimming",maskX,300,onTrackbar4)  
    cv2.createTrackbar("Mask W","Trimming",maskW,600,onTrackbar5)
    cv2.createTrackbar("Pre","Trimming",trimFrame_pre,240,onTrackbar6)
    cv2.createTrackbar("Post","Trimming",trimFrame_post,1200,onTrackbar7)
    cv2.createTrackbar("LED Color","Trimming",searchColor,2,onTrackbar8)
    cv2.createTrackbar("Gamma","Trimming",gamma,300,onTrackbar9)

    while(True):

        key = cv2.waitKey(interval)
        if key == ESC_KEY:
            break 
        elif key == R_KEY:
            interval = 0 
        elif key == enter_key:
            interval = 30
        if key == S_KEY:
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


# Create log file
def create_logFile(filename,savefile_path):
    pathTemp = [savefile_path,filename + "_trimming.log"]
    logPath = os.path.join(*pathTemp)
    f = open(logPath ,'a')
    config = filename +  "\n" + "LED th: " + str(ledTh) + ", Binary th: " + str(th_bi) + ", Height th: " + str(heightTh) + ", Pre frame: " + str(trimFrame_pre) + ", Post frame: " + str(trimFrame_post) + ", LED color: " + str(searchColor) + ", gamma: " + str(gamma) + "\n"
    f.write(config)
    f.close()
    return logPath


# Define mouse event
def get_position(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX, roiY, roiW, roiH
        roiW = 20
        roiH = 20
        roiX = x - int(roiW/2)
        roiY = y - int(roiH/2)
        frame_1st_disp  = gammaConv(gamma,frame_1st_trans.copy())
        cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
        cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
        cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
        cv2.putText(frame_1st_disp,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.imshow("Trimming",frame_1st_disp)
        display((roiX,roiY))

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
    frame_1st_disp  = gammaConv(gamma,frame_1st_trans.copy())
    cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    display("Height Th : " +  str(heightTh))

def onTrackbar4(position):
    global maskX 
    maskX = position
    frame_1st_disp  = gammaConv(gamma,frame_1st_trans.copy())
    cv2.rectangle(frame_1st_disp,(roiX,roiY),(roiX+roiW,roiY+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    display("mask X : " +  str(maskX))

def onTrackbar5(position):
    global maskW
    maskW = position
    frame_1st_disp  = gammaConv(gamma,frame_1st_trans.copy())
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    display("mask width : " +  str(maskX))

def onTrackbar6(position):
    global trimFrame_pre
    trimFrame_pre = int(position)
    display("Trimming frame pre: " + str(trimFrame_pre)) 

def onTrackbar7(position):
    global trimFrame_post
    trimFrame_post = int(position)
    display("Trimming frame post: " + str(trimFrame_post)) 

def onTrackbar8(position):
    global searchColor
    global idx
    searchColor = int(position)
    if searchColor == 0:
        idx = [0,2]
    elif searchColor == 2:
        idx = [2,0]
    display("Color: " + str(searchColor))   

def onTrackbar9(position):
    global gamma
    gamma = position/100
    frame_1st_disp = gammaConv(gamma,frame_1st_trans.copy())
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("Trimming",frame_1st_disp)
    display("Gamma : " +  str(gamma))


# Define Gamma conversion
def gammaConv(gammaVal,img):
    gamma_cvt = np.zeros((256,1), dtype=np.uint8)
    for i in range(256):
        gamma_cvt[i][0] = 255*(float(i)/255) ** (1.0 / gammaVal)
    img_gamma = cv2.LUT(img, gamma_cvt) 
    return img_gamma


def LEDdetection(filename,videofile_path,logfile_path,savefile_path):

    trigframe = 0
    sumVal = 0
    addFrame = 0
    bLED = False
    bLED_on = False

    cap = cv2.VideoCapture(videofile_path)
    totalFramenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        h, w, ch = frame.shape
        transpose_img = frame.transpose(1,0,2)
        frame_trans = transpose_img[:,::-1]
        frame_gamma = gammaConv(gamma,frame_trans)

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
        if bLED_on:
            trigframe = framenum
            f = open(logfile_path ,'a')
            config = "Trig frame: " + str(framenum) +"\n"
            f.write(config)
            f.close()

            # Background setting 
            back = np.zeros((w,h,3), dtype=np.uint8)
            mask = cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(255, 255, 255),-1)
            mask_g = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
            frame_mask = frame_gamma.copy()
            frame_mask[mask_g==0] = [0,0,0]
            frame_mask_g = cv2.cvtColor(frame_mask,cv2.COLOR_BGR2GRAY)
            frame_back =  frame_mask_g.astype(np.float32)

            # Save background image
            pathTemp = [savefile_path,filename + "_bg.jpg"]
            imgPath = os.path.join(*pathTemp)
            cv2.imwrite(imgPath,frame_gamma)

            break
        else:
            dispText = "Frame: " + str(framenum) + " / " + str(totalFramenum) +  ", LED value: " + str(sumVal)
    
        # Display
        display(dispText)    


    # Display
    dispText = filename + ", Trig: " + str(framenum)
    display(dispText)
    
    cap.release()
    return trigframe, frame_back

def differentialAnalysis(filename,videofile_path,savefile_path,trigframe,frame_back):

    sumVal = 0
    preSumVal = 0
    framenum = 0
    trialnum = 0
    x_mean = 0
    y_mean = 0
    preY_mean = 0
    x_array = []
    y_array = []
    area_array = []
    orbit = []
    startframe = []

    kernel_open = np.ones((5,5),np.uint8)
    kernel_close = np.ones((5,5),np.uint8)

    h, w = frame_back.astype(np.float32).shape
    back = np.zeros((h,w,3), dtype=np.uint8)
    mask = cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(255, 255, 255),-1)
    mask_g = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)    

    pathTemp = [savefile_path,filename + "_trajectory.csv"]
    csvPath = os.path.join(*pathTemp)
    f = open(csvPath ,'a')
    result = "Frame from trig, num_of_contours, x_mean, y_mean\n"
    f.write(result)

    cap = cv2.VideoCapture(videofile_path)
    totalFramenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES,trigframe-1)

    while(True):

        # Frame capture
        framenum += 1
        ret,frame = cap.read()
        if ret == False:
            break

        # Masking 
        transpose_img = frame.transpose(1,0,2)
        frame_trans = transpose_img[:,::-1]
        frame_gamma = gammaConv(gamma,frame_trans)
        frame_mask = frame_gamma.copy()
        frame_mask[mask_g==0] = [0,0,0]
        frame_mask_g = cv2.cvtColor(frame_mask,cv2.COLOR_BGR2GRAY)

        # Differential
        frame_diff = cv2.absdiff(frame_mask_g.astype(np.float32),frame_back)
        ret, frame_diff_bi = cv2.threshold(frame_diff, th_bi, 255, cv2.THRESH_BINARY)
        frame_diff_opening = cv2.morphologyEx(frame_diff_bi, cv2.MORPH_OPEN, kernel_open)
        frame_diff_closing = cv2.morphologyEx(frame_diff_opening, cv2.MORPH_CLOSE, kernel_close)
        frame_con, contours, hierarchy = cv2.findContours(frame_diff_closing.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find contour 
        if len(contours) == 0:
            num_contours = 0
            x_array.append(0)
            y_array.append(0)
            orbit = []
        else:
            num_contours = len(hierarchy[0])
            for cnt in contours:
                x, y, width, height = cv2.boundingRect(cnt)
                x_array.append(x+width/2)
                y_array.append(y+height/2)
                area_array.append(width*height)

        # Calculate CoG
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

        # DItect movement onset 
        if preY_mean > heightTh:
            if y_mean < heightTh:
                if y_mean > 0:
                    if trialnum == 0:
                        trialnum += 1
                        startframe.append(framenum)
                    else:
                        if framenum > startframe[trialnum-1] + trimFrame_post:
                            trialnum += 1
                            startframe.append(framenum)

        # Save
        f = open(csvPath ,'a')
        result = str(framenum) + ", " + str(num_contours) + ", " + str(x_mean) + ", " + str(y_mean)   + ",\n"
        f.write(result)
        f.close()

        # Display
        dispText = "Frame: " + str(framenum+trigframe) + " / " + str(totalFramenum) + ", Contours: " + str(num_contours)  + ' X: ' + str(x_mean) + ' Y: ' + str(y_mean) 
        display(dispText)    
        
        x_array = []
        y_array = []
        area_array = []
        preSumVal = sumVal
        preY_mean = y_mean  


    # Save
    back = np.zeros((h,w,3), dtype=np.uint8)
    for i in orbit:
        cv2.circle(back,i,3,(0,255,0),-1)
    cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    pathTemp = [savefile_path,filename + "_trajectory.jpg"]
    imgPath = os.path.join(*pathTemp)
    cv2.imwrite(imgPath,back.astype(np.uint8))

    # Display
    dispText = "Number of Trials: " + str(trialnum) + ', Start frame: ' + str(startframe)
    display(dispText)

    cap.release()
    return startframe, trialnum


def videoTrimming(fileName,videofile_path,savefile_path,logfile_path,trigframe,startframe):
    
    trimStartFrame_np = np.array(startframe)
    trimStartFrame_np = trimStartFrame_np + trigframe - trimFrame_pre
    trimStartFrame = list(trimStartFrame_np)
    trimEndFrame_np = trimStartFrame_np + trimFrame_pre + trimFrame_post
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
        dst = cv2.VideoWriter(videoSavePath, fourcc, 30.0, (h,w)) 
        
        cap.set(cv2.CAP_PROP_POS_FRAMES,trimStartFrame[i]-1)
        trimFrameNum = 0

        # Video capture
        while(True):
            framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
            ret,frame = cap.read()
            if framenum < trimEndFrame[i]:
                
                # Rotation
                transpose_img = frame.transpose(1,0,2)
                frame_trans = transpose_img[:,::-1]
                frame_gamma = gammaConv(gamma,frame_trans)
                trimFrameNum += 1
                text = fileName + " Start: " + str(trimStartFrame[i]-trigframe) + " Frame: " + str(trimFrameNum) 
                cv2.putText(frame_gamma,text,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
                dst.write(frame_gamma) 
                # Display
                dispText = "Trial: " + str(i+1)  + ", Frame: " + str(framenum) + ", Start: " + str(trimStartFrame[i]) + ", Trim: " + str(trimFrameNum)
                display(dispText)    
            else:
                break
        f = open(logfile_path ,'a')
        config = "Trial: " + str(i+1) +  ", Start frame: " + str(trimStartFrame[i]-trigframe) + ", recFrame: " + str(trimFrameNum) + "\n"
        f.write(config)
        f.close()

    pathTemp = [savePath, 'temp.avi']
    saveName = os.path.join(*pathTemp)
    dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w))
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

# Analysis
for i in range(len(files)):

    fName = os.path.basename(os.path.splitext(videoPath[i])[0])
    fNameExt = os.path.basename(os.path.splitext(videoPath[i])[1])
    pathTemp = [os.path.dirname(os.path.splitext(videoPath[i])[0]),fName + '_trimming']
    savePath = os.path.join(*pathTemp)
    os.makedirs(savePath, exist_ok=True)
    display(savePath)
    
    if i == 0:
        checkLEDPos(fName,videoPath[i])

    logPath = create_logFile(fName,savePath)

    trigFrame, frameBack = LEDdetection(fName,videoPath[i],logPath,savePath)
    startFrame, trialNum = differentialAnalysis(fName,videoPath[i],savePath,trigFrame,frameBack)

    videoTrimming(fName,videoPath[i],savePath,logPath,trigFrame,startFrame)
