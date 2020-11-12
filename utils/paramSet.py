"""
coding: UTF-8
movie trimming utils
# by Akito Kosugi 
# ver. 1.1   2020.10.24

"""

# In[Import]
import cv2
from IPython.core.display import display
from utils import framePreProcessing


# In[Initialization]
gamma = 1
rotAngle = 0
roiW = 30
roiH = 30
num_LED = 2
ledTh1 = 15
search_color1 = 1
ledTh2 = 15
search_color2 = 1
ledTh = 10
th_bi = 90
heightTh = 1075
maskX = 175
maskY = 40
trimframe_pre = 120
trimframe_post = 240

font = cv2.FONT_HERSHEY_SIMPLEX
ESC_KEY = 0x1b # Esc キー
enter_key = 13   # Enter


# In[Param set 1]
def preProcessing(filename,frame):
    global frame_1st, fName
    fName = filename
    frame_1st = frame.copy()
    frame_1st_disp = frame_1st.copy()
    h, w, ch = frame_1st.shape

    # window setting
    cv2.namedWindow("ParamSet1", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ParamSet1", w, h)
    cv2.putText(frame_1st_disp,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("ParamSet1",frame_1st)
    cv2.createTrackbar("Rot angle","ParamSet1",rotAngle,360,onTrackbar1)
    cv2.createTrackbar("gamma","ParamSet1",gamma,255,onTrackbar2)
    cv2.createTrackbar("number of LED","ParamSet1",num_LED,2,onTrackbar3)

    while(True):
        key = cv2.waitKey(0)
        if key == enter_key:
            break 

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    return rotAngle, gamma, num_LED


# In[Param set 2]
def LED(filename,frame):
    global frame_1st, fName
    fName = filename
    frame_1st = frame.copy()
    h, w, ch = frame_1st.shape
    
    # window setting
    cv2.namedWindow("ParamSet2", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ParamSet2", w, h)
    cv2.putText(frame_1st,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("ParamSet2",frame_1st)
    cv2.setMouseCallback("ParamSet2",get_position1)
    cv2.createTrackbar("LED th","ParamSet2",ledTh1,255,onTrackbar4)
    cv2.createTrackbar("Color","ParamSet2",search_color1,2,onTrackbar5)

    while(True):
        key = cv2.waitKey(0)
        if key == enter_key:
            break 

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    return roiX1, roiY1, roiW, roiH, ledTh1, search_color1


# In[Param set 3]
def trimming_LED(filename,frame):
    global frame_1st, fName
    fName = filename
    frame_1st = frame.copy()
    h, w, ch = frame_1st.shape

    # window setting
    cv2.namedWindow("ParamSet3", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ParamSet3", w, h)
    cv2.putText(frame_1st,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.imshow("ParamSet3",frame_1st)
    cv2.setMouseCallback("ParamSet3",get_position2)
    cv2.createTrackbar("LED th","ParamSet3",ledTh2,255,onTrackbar6)
    cv2.createTrackbar("Color","ParamSet3",search_color2,2,onTrackbar7)
    cv2.createTrackbar("Pre","ParamSet3",trimframe_pre,1200,onTrackbar8)
    cv2.createTrackbar("Post","ParamSet3",trimframe_post,1200,onTrackbar9)

    while(True):
        key = cv2.waitKey(0)
        if key == enter_key:
            break 

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)


    return roiX2, roiY2, roiW, roiH, ledTh2, search_color2, trimframe_pre, trimframe_post


def trimming_differential(filename,frame):
    global frame_1st, fName, maskW, maskH
    fName = filename
    frame_1st = frame.copy()
    frame_1st_disp = frame_1st.copy()
    h, w, ch = frame_1st.shape
    maskW = w - maskX*2
    maskH = h - maskY

    # window setting
    cv2.namedWindow("ParamSet3", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ParamSet3", w, h)
    cv2.putText(frame_1st_disp,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
    cv2.rectangle(frame_1st_disp,(roiX1,roiY1),(roiX1+roiW,roiY1+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.imshow("ParamSet3",frame_1st_disp)
    cv2.createTrackbar("Binary Th","ParamSet3",th_bi,255,onTrackbar10)
    cv2.createTrackbar("Height Th","ParamSet3",heightTh,h,onTrackbar11)
    cv2.createTrackbar("Mask X","ParamSet3",maskX,300,onTrackbar12)
    cv2.createTrackbar("Mask W","ParamSet3",maskW,600,onTrackbar13)
    cv2.createTrackbar("Pre","ParamSet3",trimframe_pre,360,onTrackbar8)
    cv2.createTrackbar("Post","ParamSet3",trimframe_post,2400,onTrackbar9)

    while(True):
        key = cv2.waitKey(0)
        if key == enter_key:
            break 

    cv2.waitKey(1)    
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    return th_bi, heightTh, maskX, maskY, maskW, maskH, trimframe_pre, trimframe_post


# In[GUI]
# Define mouse event
def get_position1(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX1, roiY1
        roiX1 = x - int(roiW/2)
        roiY1 = y - int(roiH/2)
        frame_1st_disp = frame_1st.copy() 
        cv2.rectangle(frame_1st_disp,(roiX1,roiY1),(roiX1+roiW,roiY1+roiH),(255,241,15),3)
        #cv2.putText(frame_1st_disp,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.imshow("ParamSet2",frame_1st_disp)
        display((roiX1,roiY1))


def get_position2(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global roiX2, roiY2
        roiX2 = x - int(roiW/2)
        roiY2 = y - int(roiH/2)
        frame_1st_disp = frame_1st.copy() 
        cv2.rectangle(frame_1st_disp,(roiX2,roiY2),(roiX2+roiW,roiY2+roiH),(255,241,15),3)
        #cv2.putText(frame_1st_disp,fName,(10,30),font,0.7,(0,0,255),2,cv2.LINE_AA)
        cv2.imshow("ParamSet3",frame_1st_disp)
        display((roiX2,roiY2))

# Define trackbar
def onTrackbar1(position):
    global rotAngle
    rotAngle = position
    display("Rotation angle: " + str(rotAngle)) 

def onTrackbar2(position):
    global gamma
    gamma = position/100
    frame_1st_disp = framePreProcessing.gammaConv(frame_1st.copy(),gamma)
    cv2.imshow("ParamSet1",frame_1st_disp)
    display("Gamma: " +  str(gamma))

def onTrackbar3(position):
    global num_LED
    num_LED = int(position)
    display("LED: " + str(num_LED)) 

def onTrackbar4(position):
    global ledTh1
    ledTh1 = position
    display("LED Th: " +  str(ledTh1))

def onTrackbar5(position):
    global search_color1
    search_color1 = int(position)
    display("Color: " + str(search_color1)) 

def onTrackbar6(position):
    global ledTh2
    ledTh2 = position
    display("LED Th: " +  str(ledTh2))

def onTrackbar7(position):
    global search_color2
    search_color2 = int(position)
    display("Color: " + str(search_color2)) 

def onTrackbar8(position):
    global trimframe_pre
    trimframe_pre = int(position)
    display("Trimming frame pre: " + str(trimframe_pre)) 

def onTrackbar9(position):
    global trimframe_post
    trimframe_post = int(position)
    display("Trimming frame post: " + str(trimframe_post)) 

def onTrackbar10(position):
    global th_bi
    th_bi = position
    display("Binary Th: " + str(th_bi))

def onTrackbar11(position):
    global heightTh 
    heightTh  = position
    frame_1st_disp = frame_1st.copy()
    cv2.rectangle(frame_1st_disp,(roiX1,roiY1),(roiX1+roiW,roiY1+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("ParamSet3",frame_1st_disp)
    display("Height Th : " +  str(heightTh))

def onTrackbar12(position):
    global maskX 
    maskX = position
    frame_1st_disp = frame_1st.copy()
    cv2.rectangle(frame_1st_disp,(roiX1,roiY1),(roiX1+roiW,roiY1+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("ParamSet3",frame_1st_disp)
    display("mask X : " +  str(maskX))

def onTrackbar13(position):
    global maskW
    maskW = position
    frame_1st_disp = frame_1st.copy()
    cv2.rectangle(frame_1st_disp,(roiX1,roiY1),(roiX1+roiW,roiY1+roiH),(255,241,15),3)
    cv2.rectangle(frame_1st_disp,(maskX,maskY),(maskX+maskW,maskY+maskH),(0,0,255),2)
    cv2.line(frame_1st_disp,(maskX,heightTh),(maskX+maskW,heightTh),(0,0,255),3)
    cv2.putText(frame_1st_disp, fName, (10, 30), font, 0.7, (0,0,255), 2, cv2.LINE_AA)
    cv2.imshow("ParamSet3",frame_1st_disp)
    display("mask width : " +  str(maskX))