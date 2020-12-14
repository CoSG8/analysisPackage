"""
coding: UTF-8
movieTrimming_differential.py
# by Akito Kosugi 
# ver. 2.1.1   2020.11.03

"""

# In[Import]
import cv2
import os
import tkinter
import tkinter.filedialog
from IPython.core.display import display

from utils import paramSet
from utils import movieAnalysis
from utils.framePreProcessing import preProcessing

# In[Initialization]
ESC_KEY = 0x1b # Esc キー
enter_key = 13   # Enter


# In[Main]
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
            if num_LED > 0:
                roiX1, roiY1, roiW, roiH, ledTh, searchColor = paramSet.LED(fName,frame_1st_process)
            th_bi, heightTh, maskX, maskY, maskW, maskH, trimFrame_pre, trimFrame_post = paramSet.trimming_differential(fName,frame_1st_process)
        
        f = open(logPath ,'a')
        config = "LED th  " + str(ledTh) + ", LED color: " + str(searchColor) + ", Binary th: " + str(th_bi) + ", Height th: " + str(heightTh)  + ", Mask X: " + str(maskX)  + ", Mask W: " + str(maskW) + ", Pre frame: " + str(trimFrame_pre) + ", Post frame: " + str(trimFrame_post) + ", gamma: " + str(gamma) + "\n"
        f.write(config)
        f.close()
        
        if num_LED > 0:
            trigFrame, trigEndFrame, frameBack = movieAnalysis.LEDdetection_1st(fName,videoPath[i],logPath,savePath,rotAngle,gamma,roiX1,roiY1,roiW,roiH,ledTh,searchColor)
        else:
            trigFrame = 1
            trigEndFrame = 1
            frameBack = frame_1st_process.copy()

        startFrame, trialNum = movieAnalysis.differential(fName,videoPath[i],savePath,trigFrame,frameBack,rotAngle,gamma,th_bi,heightTh,maskX,maskY,maskW,maskH,trimFrame_pre,trimFrame_post)
        if trialNum > 0:
            movieAnalysis.videoTrimming(fName,videoPath[i],logPath,savePath,startFrame,startFrame,trigFrame,rotAngle,gamma,trimFrame_pre,trimFrame_post)

if __name__== "__main__":
    main()