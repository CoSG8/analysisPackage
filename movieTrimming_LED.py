"""
coding: UTF-8
movieTrimming_LED.py
# by Akito Kosugi 
# ver. 2.0.2   2020.12.11

"""

# Import
import cv2
import os
import tkinter
import tkinter.filedialog
from IPython.core.display import display

from utils import paramSet
from utils import movieAnalysis
from utils.framePreProcessing import preProcessing

# Initialization
ESC_KEY = 0x1b # Esc キー
enter_key = 13   # Enter

# Main
def main():
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

        # Create log file
        pathTemp = [savePath,fName + "_trimming.log"]
        logPath = os.path.join(*pathTemp)
        f = open(logPath ,'a')
        config = fName +  "\n"
        f.write(config)
        f.close()
        
        if i == 0:
            cap = cv2.VideoCapture(videoPath[i])
            ret, frame_1st = cap.read()
            rotAngle, gamma, num_LED = paramSet.preProcessing(fName,frame_1st)
            frame_1st_process = preProcessing(frame_1st,rotAngle, gamma)
            if num_LED == 2:
                roiX1, roiY1, roiW, roiH, ledTh1, searchColor1 = paramSet.LED(fName,frame_1st_process)
            roiX2, roiY2, roiW, roiH, ledTh2, searchColor2, trimFrame_pre, trimFrame_post = paramSet.trimming_LED(fName,frame_1st_process)

        f = open(logPath ,'a')
        if num_LED == 2:
            config = "LED1 th  " + str(ledTh1) + ", LED1 color: " + str(searchColor1) + ", LED2 th  " + str(ledTh2) + ", LED2 color: " + str(searchColor2) + ", Pre frame: " + str(trimFrame_pre) + ", Post frame: " + str(trimFrame_post) + ", gamma: " + str(gamma) + "\n"
        elif num_LED == 1:
            config = "LED1 th  " + str(ledTh2) + ", LED1 color: " + str(searchColor2) + ", Pre frame: " + str(trimFrame_pre) + ", Post frame: " + str(trimFrame_post) + ", gamma: " + str(gamma) + "\n"            
        f.write(config)
        f.close()

        if num_LED == 2:
            if i == 0:
                trigFrame, trigEndFrame, frameBack = movieAnalysis.LEDdetection_1st(fName,videoPath[i],logPath,savePath,rotAngle,gamma,roiX1,roiY1,roiW,roiH,ledTh1,searchColor1)
            else:
                trigFrame = 0
                trigEndFrame = 0
        else:
            trigFrame = 0
            trigEndFrame = 0

        startFrame, endFrame,trialNum = movieAnalysis.LEDdetection(fName,videoPath[i],savePath,trigFrame,trigEndFrame,rotAngle,gamma,roiX2,roiY2,roiW,roiH,ledTh2,searchColor2,trimFrame_pre,trimFrame_post)
        if trialNum > 0:
            movieAnalysis.videoTrimming(fName,videoPath[i],logPath,savePath,startFrame,endFrame,trigFrame,rotAngle,gamma,trimFrame_pre,trimFrame_post)

if __name__== "__main__":
    main()