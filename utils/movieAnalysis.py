"""
coding: UTF-8
movie trimming utils
# by Akito Kosugi 
# ver. 1.2.8   2021.01.04

"""

# In[Import]
import cv2
import os
import numpy as np
from IPython.core.display import display

from utils.framePreProcessing import preProcessing


# In[Initialization]
font = cv2.FONT_HERSHEY_SIMPLEX
fourcc = cv2.VideoWriter_fourcc(*"MJPG")

ESC_KEY = 0x1b # Esc キー
enter_key = 13   # Enter


# In[1st Processiong]
def LEDdetection_1st(filename,videofile_path,logfile_path,savefile_path,rotAngle,gamma,roiX1,roiY1,roiW,roiH,ledTh1,searchColor1):
     # Initialization
    trigframe = 0
    trigEnd_frame = 0
    sumVal = 0
    bLED = False
    bLED_on = False
    bLED_off = False

    cap = cv2.VideoCapture(videofile_path,cv2.CAP_FFMPEG)
    totalFramenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while(True):

        # Video capture
        framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        ret, frame = cap.read()
        h, w, ch = frame.shape
        frame_process = preProcessing(frame,rotAngle,gamma) 

        # LED Detection
        roiFrame = frame_process[roiY1:roiY1+roiH,roiX1:roiX1+roiW]
        if searchColor1 < 2:
            sumVal = roiFrame.T[searchColor1].flatten().mean() - roiFrame.T[2].flatten().mean()
        else:
            sumVal = roiFrame.T[searchColor1].flatten().mean() - roiFrame.T[1].flatten().mean()            
        if sumVal > ledTh1:
            if bLED == False:
                bLED_on = True
            bLED = True
        else:
            if bLED:
                bLED_off = True
            bLED = False

        if bLED_on:
            trigframe = framenum
            f = open(logfile_path ,'a')
            config = "Trig frame: " + str(framenum) +"\n"
            f.write(config)
            f.close()

            # Background setting 
            frame_back = frame_process.copy()

            # Save background image
            pathTemp = [savefile_path,filename + "_bg.jpg"]
            imgPath = os.path.join(*pathTemp)
            cv2.imwrite(imgPath,frame_process)
            bLED_on = False
        elif bLED_off:
            trigEnd_frame = framenum
            break
       
        # Display
        dispText = "Frame: " + str(framenum) + " / " + str(totalFramenum) +  ", LED value: " + str(sumVal)
        display(dispText)    

    # Display
    dispText = filename + ", Trig: " + str(trigframe)
    display(dispText)
    
    cap.release()
    return trigframe, trigEnd_frame, frame_back


# In[2nd Processiong]
def LEDdetection(filename,videofile_path,savefile_path,trigframe,trigEnd_frame,rotAngle,gamma,roiX2,roiY2,roiW,roiH,ledTh2,searchColor2,trimFrame_pre,trimFrame_post):
    # Initialization
    startframe = []
    endframe = []
    duration = []
    trialNum = 0
    frameNum = 0
    sumVal = 0
    addFrame = 0
    bLED = False
    bLED_on = False
    bLED_off = False

    cap = cv2.VideoCapture(videofile_path)
    totalFrameNum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if trigEnd_frame>0:
        cap.set(cv2.CAP_PROP_POS_FRAMES,trigEnd_frame-1)
    frameNum = trigEnd_frame-trigframe

    while(True):

        # Video capture
        ret, frame = cap.read()
        if ret == False:
            if bLED:
                endframe.append(frameNum)
                duration.append(addFrame)
            break
        else:
            frameNum += 1
        frame_process = preProcessing(frame,rotAngle,gamma) 

        # LED Detection
        roiFrame = frame_process[roiY2:roiY2+roiH,roiX2:roiX2+roiW]
        if searchColor2 < 2:
            sumVal = roiFrame.T[searchColor2].flatten().mean() - roiFrame.T[2].flatten().mean()
        else:
            sumVal = roiFrame.T[searchColor2].flatten().mean() - roiFrame.T[1].flatten().mean()            
        if sumVal > ledTh2:
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

    # Display
    dispText = "Number of Trials: " + str(trialNum) + ', Start frame: ' + str(startframe) + ', End frame: ' + str(endframe)
    display(dispText)
    
    cap.release()
    return startframe, endframe, trialNum


def differential(filename,videofile_path,savefile_path,trigframe,frameback,rotAngle,gamma,th_bi,heightTh,maskX,maskY,maskW,maskH,trimFrame_pre,trimFrame_post):

    framenum = 0
    trialnum = 0
    maskY = 40    
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

    # Background setting 
 #   h, w = frameback.astype(np.float32).shape()
    h, w, ch = frameback.shape
    maskH = h - maskY
    back = np.zeros((h,w,3), dtype=np.uint8)
    mask = cv2.rectangle(back,(maskX,maskY),(maskX+maskW,maskY+maskH),(255, 255, 255),-1)
    mask_g = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    frame_mask = frameback.copy()
    frame_mask[mask_g==0] = [0,0,0]
    frame_mask_g = cv2.cvtColor(frame_mask,cv2.COLOR_BGR2GRAY)
    frame_back =  frame_mask_g.astype(np.float32)

    pathTemp = [savefile_path,filename + "_trajectory.csv"]
    csvPath = os.path.join(*pathTemp)
    f = open(csvPath ,'a')
    result = "Frame from trig, num_of_contours, x_mean, y_mean\n"
    f.write(result)

    cap = cv2.VideoCapture(videofile_path)
    totalFramenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES,trigframe)

    while(True):
        # Frame capture
        ret,frame = cap.read()
        if ret == False:
            break
        else:
            framenum += 1

        # Masking 
        frame_mask = preProcessing(frame,rotAngle,gamma)
        frame_mask[mask_g==0] = [0,0,0]
        frame_mask_g = cv2.cvtColor(frame_mask,cv2.COLOR_BGR2GRAY)

        # Differential
        frame_diff = cv2.absdiff(frame_mask_g.astype(np.float32),frame_back)
        ret, frame_diff_bi = cv2.threshold(frame_diff, th_bi, 255, cv2.THRESH_BINARY)
        frame_diff_opening = cv2.morphologyEx(frame_diff_bi, cv2.MORPH_OPEN, kernel_open)
        frame_diff_closing = cv2.morphologyEx(frame_diff_opening, cv2.MORPH_CLOSE, kernel_close)
#        frame_con, contours, hierarchy = cv2.findContours(frame_diff_closing.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(frame_diff_closing.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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


def frameDisp(frame,filename,numFrame,totalNumFrame,bRecording):

    cv2.putText(frame,filename,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    msg = "s key: play or stop, r key: trim start or stop"
    cv2.putText(frame, msg, (10, 60), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    msg = "enter key: next frame, space key: previous frame"
    cv2.putText(frame, msg, (10, 80), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    msg = "Frame: " + str(int(numFrame)) + " / " + str(int(totalNumFrame))
    cv2.putText(frame, msg, (30, 110), font, 0.5, (0,0,255), 2, cv2.LINE_AA)
    if(bRecording):
        cv2.circle(frame,(15,105),10,(0,0,255),thickness=-1)
    cv2.imshow("img",frame)
    
def manualAnnotation(filename,videofile_path,savefile_path,trigframe,rotAngle,gamma):
    
    ESC_KEY = 27 # Esc キー
    space_KEY = 32   # Space
    enter_KEY = 13   # Enter
    s_KEY = ord('s')
    r_KEY = ord('r')
    a_KEY = ord('a')
    interval = 0
    trialNum = 0
    startframe = []
    endframe = []
    bRecording = False
    bPlaying = False
    bPlaying_fast = False

    cap = cv2.VideoCapture(videofile_path)
    totalNumFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES,trigframe)

    ret,frame = cap.read() 
    frame_process = preProcessing(frame,rotAngle,gamma) 
    numFrame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    h,w,ch = frame_process.shape
    cv2.namedWindow("img",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("img",w,h)
    frameDisp(frame_process,filename,numFrame,totalNumFrame,bRecording)

    while(True):
        # Video capture
        ret, frame = cap.read()
        if ret == False:
            break

        framenum = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + 1
        frame_process = preProcessing(frame,rotAngle,gamma) 
        frameDisp(frame_process,filename,framenum,totalNumFrame,bRecording)

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
                startframe.append(framenum)
                trialNum += 1
                display("Trim " + str(len(startframe)) + " start: " + str(int(framenum)) + " frame")
            else:
                endframe.append(framenum)
                display("Trim " + str(len(startframe)) + " stop: " + str(int(framenum)) + " frame")
            setframe = framenum-3
            cap.set(cv2.CAP_PROP_POS_FRAMES,setframe)
            ret, frame = cap.read()
            numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            frame_process = preProcessing(frame,rotAngle,gamma) 
            frameDisp(frame_process,filename,numFrame,totalNumFrame,bRecording)
        elif key == space_KEY:
            setframe = framenum-4
            cap.set(cv2.CAP_PROP_POS_FRAMES,setframe)
            ret, frame = cap.read()
            numFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            frame_process = preProcessing(frame,rotAngle,gamma) 
            frameDisp(frame_process,filename,numFrame,totalNumFrame,bRecording)

    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    # Display
    trialnum = len(startframe)
    dispText = "Number of Trials: " + str(trialnum) + ', Start frame: ' + str(startframe)
    display(dispText)
    
    cap.release()
    return startframe, endframe, trialnum


# In[3rd Processiong]
def videoTrimming(filename,videofile_path,logfile_path,savefile_path,startframe,endframe,trigframe,rotAngle,gamma,trimframe_pre,trimframe_post):
    # Initialization
    trimStartFrame_np = np.array(startframe)
    trimStartFrame_np = trimStartFrame_np + trigframe - trimframe_pre
    trimStartFrame = list(trimStartFrame_np)
    trimEndFrame_np = np.array(endframe)    
    trimEndFrame_np = trimEndFrame_np + trigframe + trimframe_post
    trimEndFrame = list(trimEndFrame_np)

    cap = cv2.VideoCapture(videofile_path)
    totalframenum = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ret, frame = cap.read() 
    frame_process = preProcessing(frame,rotAngle,gamma) 
    h, w, ch = frame_process.shape
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    trialnum = len(trimStartFrame)

    # Trimming
    for i in range(trialnum):
        if i < 9:
            pathTemp = [savefile_path,filename + "_trial_0" + str(i+1) + ".avi"]
        else:
            pathTemp = [savefile_path,filename + "_trial_" + str(i+1) + ".avi"]
        videoSavePath = os.path.join(*pathTemp)
        dst = cv2.VideoWriter(videoSavePath, fourcc, 30.0, (w,h)) 
        
        cap.set(cv2.CAP_PROP_POS_FRAMES,trimStartFrame[i]-1)
        trimFrameNum = 0

        # Video capture
        while(True):
            ret,frame = cap.read()
            frameNum = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            if frameNum > totalframenum-2:
            	break
            elif frameNum < trimEndFrame[i]:
                frame_process = preProcessing(frame,rotAngle,gamma) 
                trimFrameNum += 1
                text = filename + " Start: " + str(trimStartFrame[i]-trigframe) + " Frame: " + str(trimFrameNum) 
                cv2.putText(frame_process,text,(10,30),font,0.6,(0,0,255),2,cv2.LINE_AA)
                dst.write(frame_process) 
                # Display
                dispText = "Trial: " + str(i+1)  + ", Frame: " + str(frameNum) + ", Start: " + str(trimStartFrame[i]-trigframe) + ", Trim: " + str(trimFrameNum)
                display(dispText)    
            else:
                break

    pathTemp = [savefile_path, 'temp.avi']
    saveName = os.path.join(*pathTemp)
    dst = cv2.VideoWriter(saveName, fourcc, 30.0, (h,w))
#     os.remove(saveName)
    
    cap.release()
    
    # write log file
    f = open(logfile_path ,'a')
    msg = "Total frame: " + str(totalframenum) + "\n"
    f.write(msg)
    for i in range(trialnum):
        result = "Trial: " + str(i+1) + ", Start time from trig: " + str("{0:6.1f}".format((startframe[i]+1)/fps)) + " s , Start frame: " + str(trimStartFrame[i]-trigframe) + ", End frame: " + str(trimEndFrame[i]-trigframe) + ", Duration: " + str(trimEndFrame[i]-trimStartFrame[i]+1) +"\n"
        f.write(result)
    f.close()