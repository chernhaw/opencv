import cv2
print(cv2.__version__)
import numpy as np
import Jetson 

import time
from adafruit_servokit import ServoKit

def nothing(x):
    pass

cv2.namedWindow('Trackbars')
cv2.moveWindow('Trackbars',1320,0)

cv2.createTrackbar('hueLower', 'Trackbars',28,179,nothing)
cv2.createTrackbar('hueUpper', 'Trackbars',114,179,nothing)

cv2.createTrackbar('hue2Lower', 'Trackbars',71,179,nothing)
cv2.createTrackbar('hue2Upper', 'Trackbars',5,179,nothing)

cv2.createTrackbar('satLow', 'Trackbars',40,255,nothing)
cv2.createTrackbar('satHigh', 'Trackbars',84,255,nothing)
cv2.createTrackbar('valLow','Trackbars',80,255,nothing)
cv2.createTrackbar('valHigh','Trackbars',118,255,nothing)



dispW=640
dispH=480
flip=2
#Uncomment These next Two Line for Pi Camera
# camSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'
# cam= cv2.VideoCapture(camSet)
kit= ServoKit(channels=16)
#Or, if you have a WEB cam, uncomment the next line
#(If it does not work, try setting to '1' instead of '0')
cam=cv2.VideoCapture(0)
width=cam.get(cv2.CAP_PROP_FRAME_WIDTH)
height=cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
print('width: ',width,' height: ',height)
pan=0
tilt=90

while True:
    ret, frame = cam.read()
    #frame=cv2.imread('smarties.png')
    cv2.imshow('nanoCam',frame)
    cv2.moveWindow('nanoCam',0,0)

    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    hueLow=cv2.getTrackbarPos('hueLower', 'Trackbars')
    hueUp=cv2.getTrackbarPos('hueUpper', 'Trackbars')

    hue2Low=cv2.getTrackbarPos('hue2Lower', 'Trackbars')
    hue2Up=cv2.getTrackbarPos('hue2Upper', 'Trackbars')

    Ls=cv2.getTrackbarPos('satLow', 'Trackbars')
    Us=cv2.getTrackbarPos('satHigh', 'Trackbars')

    Lv=cv2.getTrackbarPos('valLow', 'Trackbars')
    Uv=cv2.getTrackbarPos('valHigh', 'Trackbars')

    l_b=np.array([hueLow,Ls,Lv])
    u_b=np.array([hueUp,Us,Uv])

    l_b2=np.array([hue2Low,Ls,Lv])
    u_b2=np.array([hue2Up,Us,Uv])

    FGmask=cv2.inRange(hsv,l_b,u_b)
    FGmask2=cv2.inRange(hsv,l_b2,u_b2)
    FGmaskComp=cv2.add(FGmask,FGmask2)
   # cv2.imshow('FGmaskComp',FGmaskComp)
    #cv2.moveWindow('FGmaskComp',0,250)

    FG=cv2.bitwise_and(frame, frame, mask=FGmaskComp)
   # cv2.imshow('FG',FG)
    #cv2.moveWindow('FG',400,0)

    bgMask=cv2.bitwise_not(FGmaskComp)
   # cv2.imshow('bgMask',bgMask)
    #cv2.moveWindow('bgMask',0,500)

    BG=cv2.cvtColor(bgMask,cv2.COLOR_GRAY2BGR)

    final=cv2.add(FG,BG)
    cv2.imshow('final',final)
   # cv2.moveWindow('final',900,0)
    
    contours,hierarchy = cv2.findContours(FGmaskComp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

   # print(contours)
    
    kit.servo[13].angle = 0
    kit.servo[15].angle =0
    contours=sorted(contours,key=lambda x:cv2.contourArea(x),reverse=True)
    for cnt in contours:
        area=cv2.contourArea(cnt)

        (x,y,w,h)=cv2.boundingRect(cnt)
        print(f"x={x}")
        print(f"y={y}")

        print(f"tilt {tilt}")
        print(f"pan {pan}")
        if area>=200:
            cv2.rectangle(frame,(x,y),(x+w,y+h), (255,0,0),3)         

            objX=x+w/2
            objY=y+h/2


            errorPan =objX-width/2
            errorTilt = objY+height/2

            if errorPan > 0:
                pan=pan-1   

            if errorPan<0:
                pan = pan +1

            if errorTilt >0:
                tilt=tilt+1

            if errorTilt <0:
                tilt=tilt-1

            print(pan)
            print(tilt)
            
            if pan > 150:
                pan= 150
                print("Pan out of range")
            if pan < 0:
                pan= 0
                print("Pan out of range")

            if tilt > 150:
                tilt= 150
                print("Tilt out of range")
            if tilt < 0:
                tilt= 0
                print("Tilt out of range")
            
            kit.servo[13].angle =pan
            kit.servo[15].angle =tilt
            break
            

    cv2.drawContours(frame,contours,0,(255,0,0),3)
    cv2.imshow('frame',frame)

   
    if cv2.waitKey(1)==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()


#/usr/local/lib/python3.6/dist-packages/
# sudo chown chernhaw /home/chernhaw/.local/lib/python3.6/site-packages/Jetson/GPIO/
# sudo chown chernhaw /usr/local/lib/python3.6/dist-packages/adafruit_blinka/microcontroller/tegra/t210/pin.py
# sudo chown chernhaw /usr/local/lib/python3.6/dist-packages/adafruit_blinka/board/nvidia/jetson_nano.py
# /usr/local/lib/python3.6/dist-packages/adafruit_blinka/board/nvidia/jetson_nano.py
# /usr/local/lib/python3.6/dist-packages/adafruit_servokit.py

#  sudo chown chernhaw /usr/local/lib/python3.6/dist-packages/adafruit_servokit.py


# sudo chmod 755 /home/chernhaw/.local/lib/python3.6/site-packages/Jetson/GPIO/
# sudo  chmod 755 /usr/local/lib/python3.6/dist-packages/adafruit_blinka/microcontroller/tegra/t210/pin.py
# sudo chmod  755 /usr/local/lib/python3.6/dist-packages/adafruit_blinka/board/nvidia/jetson_nano.py
# /usr/local/lib/python3.6/dist-packages/adafruit_blinka/board/nvidia/jetson_nano.py
# /usr/local/lib/python3.6/dist-packages/adafruit_servokit.py
#  sudo chmod 755 /usr/local/lib/python3.6/dist-packages/adafruit_servokit.py
# sudo chmod 755 /home/chernhaw/.local/lib/python3.6/site-packages/Jetson/GPIO/gpio.py
