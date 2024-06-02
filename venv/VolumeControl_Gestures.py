import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Define webcam params:
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

# Instantiate hand detector class
detector = htm.FindHands(detection_con=0.7);

# Pycaw - control PC functionality:
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPercentage = 0

# Gesture detection logic
while True:
    success, img = cap.read()

    if success:
        # Draw circles around index and thumb:
        landmarks = detector.getPosition(img, [4,8])
        for point in landmarks:
            cv2.circle(img, point, 10, (0, 255, 0), cv2.FILLED)

        # Draw a line between 2 circles
        if len(landmarks) != 0:
            cv2.line(img, landmarks[0], landmarks[1], (255,0,255), 3)

            # Define coordinates:
            x1, y1 = landmarks[0][0], landmarks[0][1]
            x2, y2 = landmarks[1][0], landmarks[1][1]
            # Add circle in the center of the line and draw a circle at the midpoint:
            mid_x = int((x1 + x2) / 2)
            mid_y = int((y1 + y2) / 2)
            cv2.circle(img, (mid_x, mid_y), 10, (0, 0, 255), cv2.FILLED)

            length = math.hypot(x2-x1, y2-y1)

            # Converter:
            # Hand range 50 - 300
            # Volume range -65 - 0
            vol = np.interp(length,[50,300],[minVol,maxVol])
            volBar = np.interp(length,[50,300],[400,150])
            volPercentage = np.interp(length,[50,300],[0,100])

            print (vol)
            volume.SetMasterVolumeLevel(vol, None)

            if length<50:
                cv2.circle(img, (mid_x, mid_y), 10, (0, 255, 0), cv2.FILLED)

        # Add volume bar:
        cv2.rectangle(img, (50,150), (85,400),(255, 0, 0), 3)
        cv2.rectangle(img, (50,int(volBar)), (85,400),(255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'Volume: {int(volPercentage)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 2)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 2)

        cv2.imshow("Img", img)
    else:
        print("Failed to capture image")
        break
    cv2.waitKey(1)
