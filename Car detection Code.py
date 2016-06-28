
import RPi.GPIO as GPIO
import numpy as np
import argparse
import imutils
import cv2
import picamera
import sys
import time
import math
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera import PiCamera
led = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(led,GPIO.OUT)

from imutils.video import VideoStream



PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range


ap = argparse.ArgumentParser()
ap.add_argument("-p","--picamera", type=int, default=-1, help="wether or not")
args = vars(ap.parse_args())


whiteLower = (0, 0, 240)      
whiteUpper = (180, 25, 255)   

#blueLower = ( 105, 100, 50)   
#blueUpper = (120, 255, 255)    

camera=VideoStream(usePiCamera=args["picamera"] > 0).start()


time.sleep(1.0)
fps = FPS().start()

while(True):
    
        
	frame = camera.read()       
	
	frame = imutils.resize(frame, width=400)
        blurred = cv2.GaussianBlur(frame,(11,11),0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
#	bmask = cv2.inRange(hsv, blueLower, blueUpper)
#	bmask = cv2.erode(bmask, None, iterations=2)
#	bmask = cv2.dilate(bmask, None, iterations=2)

	mask = cv2.inRange(hsv, whiteLower, whiteUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

 #       tmask = mask + bmask
      #  cv2.imshow('tmask',mask)
	
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
        center1 = None
    	r1,r2,=(0,0)
	a1,b1,a2,b2 =(0,0,0,0)
	
	m=[]
	n=[]
	r=[]
	cen=[]
	font = cv2.FONT_HERSHEY_SIMPLEX
	vehicle=0
	a,b,w,h = (0,0,0,0)
	if len(cnts) > 0:
            L=len(cnts)
     
            cv2.putText(frame,str(L),(20,20),font,1,(0,0,255),2)
		
            for p in range(0,L,1):
                c=cnts[p]
                ((x, y), radius1) = cv2.minEnclosingCircle(c)     
                m.append(int(x))
                n.append(int(y))
                r.append(int(radius1))

                M = cv2.moments(c)
                center1 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cen.append(center1)
            
                if radius1 >1:
                        
                    cv2.circle(frame, (int(x), int(y)), int(radius1),(0, 255, 255), 2)
                    cv2.circle(frame, center1, 5, (0, 0, 255), -1)
                    cv2.putText(frame,str(p),(int(x),int(y)),font,1,(255,255,255),2)      
                
        e=len(cnts)
        if(e==1 or e==0):
            GPIO.output(led,False)
        if(e>=8):
            GPIO.output(led,False)
        if(e>1 and e<8):
            for i in range(0,e-1,1):
                for j in range(i+1,e,1):
                    a1=float(m[i])
                    b1=float(n[i])
                    a2=float(m[j])
                    b2=float(n[j])
                    r1=float(r[i])
                    r2=float(r[j])
                    if((a2-a1)!=0):              
                        angle = int(math.atan((b1-b2)/(a2-a1))*180/math.pi)
                    if(angle>-5 and angle<5):
                        cv2.line(frame,cen[i],cen[j],(0,255,0),2)
                        cv2.putText(frame,str(angle),(int(a1)+50,(int(b2)+int(b1))/2),font,1,255,2)
                        a1=int(m[i])
                        b1=int(n[i])
                        a2=int(m[j])
                        b2=int(n[j])
                        r1=int(r[i])
                        r2=int(r[j])
                        if(r1>r2):
                            p=r1-r2
                            h=2*r1
                        if(r2>r1):
                            p=r2-r1
                            h=2*r2
                        if(r1==r2):
                            h=2*r1
                            p=0
                        if(p<10 and cen[i]!=0 and cen[j]!=0):
                            vehicle = vehicle + 1
                            if(a2>a1):
                                w=r1+r2+(a2-a1)
                                (a,b) = (a1-r1,b1-r1)
                                
                            if(a1>a2):
                                w=r1+r2+(a1-a2)
                                (a,b) = (a2-r2,b2-r2)
                                
                                                      
                                cv2.rectangle(frame,(a,b),(a+w,b+h),(0,0,255),2)
                                cv2.putText(frame,"vehicle detected",(20,250),font,1,(0,255,0),2)
                                cv2.putText(frame,str(vehicle),(5,250),font,1,(0,255,0),2)
                               
                                GPIO.output(led,True)
                            else:
                       
                                GPIO.output(led,False)
                        else:
                            GPIO.output(led,False)
                       
       
                
            
        
	
        cv2.imshow("Frame", frame)  
        fps.update()
        key = cv2.waitKey(1) & 0xFF
        
	
        if key == ord("q"):
            GPIO.cleanup()
            
            fps.stop()
            print("############### appx fps {:.2f}".format(fps.fps()))
            break


camera.stop()
cv2.destroyAllWindows()
