import cv2
import math
import time
import mediapipe as mp
from os import listdir

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
print(minVol, maxVol)


def calAngle(pt1, pt2, pt3):
    # print('---------')
    a = math.sqrt(math.pow(pt2[1] - pt1[1], 2) + math.pow(pt2[0] - pt1[0], 2))
    b = math.sqrt(math.pow(pt3[1] - pt2[1], 2) + math.pow(pt3[0] - pt2[0], 2))
    c = math.sqrt(math.pow(pt1[1] - pt3[1], 2) + math.pow(pt1[0] - pt3[0], 2))
    # print(a,b,c)
    angle = math.acos((a * a + b * b - c * c) / (2 * a * b)) * 180 / math.pi
    # print(angle)
    return angle


def Normalize_landmarks(image, hand_landmarks):
    new_landmarks = []
    for i in range(0, len(hand_landmarks.landmark)):
        float_x = hand_landmarks.landmark[i].x
        float_y = hand_landmarks.landmark[i].y
        width = image.shape[1]
        height = image.shape[0]
        pt = mp_drawing._normalized_to_pixel_coordinates(float_x, float_y, width, height)
        new_landmarks.append(pt)
    return new_landmarks


def Draw_hand_points(image, normalized_hand_landmarks):
    cv2.circle(image, normalized_hand_landmarks[4], 12, (255, 0, 255), -1, cv2.LINE_AA)
    cv2.circle(image, normalized_hand_landmarks[8], 12, (255, 0, 255), -1, cv2.LINE_AA)
    cv2.line(image, normalized_hand_landmarks[4], normalized_hand_landmarks[8], (255, 0, 255), 3)
    x1, y1 = normalized_hand_landmarks[4][0], normalized_hand_landmarks[4][1]
    x2, y2 = normalized_hand_landmarks[8][0], normalized_hand_landmarks[8][1]
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 100:
        cv2.circle(image, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
    else:
        cv2.circle(image, (cx, cy), 12, (255, 0, 255), cv2.FILLED)
    return image, length


pTime = 0

hands = mp_hands.Hands(
    min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("camera frame is empty!")
        continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            normalized_landmarks = Normalize_landmarks(image, hand_landmarks)

            try:
                image, length = Draw_hand_points(image, normalized_landmarks)
                # print(length) #20~300
                cv2.rectangle(image, (50, 150), (85, 350), (255, 0, 0), 3)
                if length > 200:
                    length = 200

                # Hand range 0 - 210
                # Volume Range -65 - 0
                vol = int((200 - length) / 200 * (minVol))
                # print(vol)
                volume.SetMasterVolumeLevel(vol, None)

                cv2.rectangle(image, (50, int(350 - length)), (85, 350), (255, 0, 0), cv2.FILLED)
                percent = int(length / 200.0 * 100)
                # print(percent)
                if percent > 100:
                    percent = 100
                strRate = str(percent) + '%'
                cv2.putText(image, strRate, (40, 410), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 0, 0), 2)
                cTime = time.time()
                fps = 1 / (cTime - pTime)
                pTime = cTime
                cv2.putText(image, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 0, 0), 2)
            except:
                pass

    cv2.imshow('result', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break
cv2.destroyAllWindows()
hands.close()
cap.release()