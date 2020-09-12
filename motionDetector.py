import cv2
from pythonosc import udp_client

ip = "192.168.20.16"
port = 6868
client = udp_client.SimpleUDPClient(ip, port)
print("Sending osc to", ip, "port:", port)
stillnessCount = 0
stillnessThreshold = 100  # number of frames of stillness before sending OSC message

cap = cv2.VideoCapture(0)  # change index until you get the cam you want
ret1, frame1 = cap.read()
baseFrame = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
baseFrame = cv2.GaussianBlur(baseFrame, (21, 21), 0)
cv2.imshow('window', frame1)
frameCount = 0

while(True):
    ret2, frame2 = cap.read()
    currentFrame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    currentFrame = cv2.GaussianBlur(currentFrame, (21, 21), 0)

    # reset the base frame periodically
    if frameCount == 40:
        baseFrame = currentFrame
        frameCount = 0

    deltaframe = cv2.absdiff(baseFrame, currentFrame)
    threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None)
    contour, heirarchy = cv2.findContours(
        threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contour) > 0:
        stillnessCount = 0
    else:
        stillnessCount += 1
    if stillnessCount == stillnessThreshold:
        client.send_message("/isMotionDetected", False)
    if stillnessCount == 0:
        client.send_message("/isMotionDetected", True)

    for i in contour:
        if cv2.contourArea(i) < 50:
            continue
        (x, y, w, h) = cv2.boundingRect(i)
        cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imshow('window', frame2)
    frameCount += 1

    if cv2.waitKey(20) == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
