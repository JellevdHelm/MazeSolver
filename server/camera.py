import cv2
import mqtt as m
import json
import numpy as np 

from pathplanner import Directions

path = "server/resources/blueTestImage.jpeg"

mazeWidth = mazeHeight = 600    # Aspect ratio 
outputWindowWidth = outputWindowHeight = mazeWidth

upperLeft = [316, 270]
upperRight = [370, 264] 
lowerLeft = [319, 319]
lowerRight = [373, 317]

directions = {
    range(45, 135): Directions.NORTH.name,
    range(-45, 45): Directions.EAST.name,
    range(-135, -45): Directions.SOUTH.name,
    range(135, 181): Directions.WEST.name,
    range(-179, -135): Directions.WEST.name
}

def emptyfun(x):
    pass

class Camera:
    cameraSource = 1
    camWidth = 640
    camHeigth = 480

    satAdjustment = 1
    valAdjustment = 1

    yellowMaskLower = np.array([10, 115, 80])
    yellowMaskUpper = np.array([25, 255, 255])

    blueMaskLower = np.array([90, 90, 170])
    blueMaskUpper = np.array([120, 255, 255])

    redMaskLower = np.array([160, 60, 150])
    redMaskUpper = np.array([179, 255, 255])

    greenMaskLower = np.array([65, 100, 155])
    greenMaksUpper = np.array([90, 255, 255])

    pinkMaskLower = np.array([149, 30, 220])
    pinkMaskUpper = np.array([179, 232, 255])

    def __init__(self):
        self.cam = cv2.VideoCapture(self.cameraSource)
        self.cam.set(3, self.camWidth)
        self.cam.set(4, self.camHeigth)
        self.cam.set(10, 60)
        self.client = m.Mqtt("Camera", self.on_connect, self.on_message)
        self.client.connectMQTT()
        pass

    ### Run modes
    def run(self):
        while True:
            input, output = self.getImage(self.yellowMaskLower, self.yellowMaskUpper)

            cv2.imshow("Input image", input)
            cv2.imshow("Output image", output)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break         

    def calibrateColors(self):
        cv2.namedWindow("TrackBar")
        cv2.resizeWindow("TrackBar", 640, 480)
        cv2.createTrackbar("Hue min", "TrackBar", 28, 179, emptyfun)
        cv2.createTrackbar("Hue max", "TrackBar", 35, 179, emptyfun)
        cv2.createTrackbar("Sat min", "TrackBar", 80, 255, emptyfun)
        cv2.createTrackbar("Sat max", "TrackBar", 255, 255, emptyfun)
        cv2.createTrackbar("Val min", "TrackBar", 235, 255, emptyfun)
        cv2.createTrackbar("Val max", "TrackBar", 255, 255, emptyfun)

        while True:
            hMin = cv2.getTrackbarPos("Hue min", "TrackBar")
            hMax = cv2.getTrackbarPos("Hue max", "TrackBar")
            sMin = cv2.getTrackbarPos("Sat min", "TrackBar")
            sMax = cv2.getTrackbarPos("Sat max", "TrackBar")
            vMin = cv2.getTrackbarPos("Val min", "TrackBar")
            vMax = cv2.getTrackbarPos("Val max", "TrackBar")

            lower = np.array([hMin, sMin, vMin])
            upper = np.array([hMax, sMax, vMax])

            input, output = self.getImage(lower, upper)

            cv2.imshow("Input image", input)
            cv2.imshow("Output image", output)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def calibrateColorAdjustment(self):
        cv2.namedWindow("TrackBar")
        cv2.resizeWindow("TrackBar", 640, 120)
        cv2.createTrackbar("Sat adjustment", "TrackBar", 0, 250, emptyfun)
        cv2.createTrackbar("Val adjustment", "TrackBar", 250, 250, emptyfun)

        while True:
            self.satAdjustment = cv2.getTrackbarPos("Sat adjustment", "TrackBar") / 50
            self.valAdjustment = cv2.getTrackbarPos("Val adjustment", "TrackBar") / 250
            print("Sat: ", self.satAdjustment)
            print("Val: ", self.valAdjustment)
            
            success, img = self.cam.read()
            # img = cv2.imread(path)
            # img = cv2.resize(img, (640, 480))

            imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            imgHSV = self.applySaturationAjustment(imgHSV)
            
            img2 = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
            
            cv2.imshow("Input image", img)
            cv2.imshow("Output image", img2)
            cv2.imshow("HSV", imgHSV)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # TODO: Change to set function and run when camera starts to flatten maze(?)
    def getMazeCorners(self):
        # img = cv2.imread(path)
        # img = cv2.resize(img, (640, 480))
        while True:
            success, img = self.cam.read()
            cv2.imshow("Maze corners", img)
            cv2.setMouseCallback("Maze corners", self.mouseEvent)
            
            img2 = self.transformPerspective(img)
            cv2.imshow("Transformed", img2)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    
    ### Camera functions
    def getCoordinates(self, carNumber):
        # Depending on received message call getImage with the right color masks for the car
        coords1 = None
        coords2 = None

        # TODO: If server receives lots of arrays/values, one reason may be the mask not finding anything or too much, Remove after project 
        if carNumber == 0:
            coords1 = self.getImage(self.blueMaskLower, self.blueMaskUpper, getCoords = True)
            coords2 = self.getImage(self.yellowMaskLower, self.yellowMaskUpper, getCoords = True)
        elif carNumber == 1:
            coords1 = self.getImage(self.redMaskLower, self.redMaskUpper, getCoords = True)
            coords2 = self.getImage(self.greenMaskLower, self.greenMaksUpper, getCoords = True)

        try:
            vector = coords2 - coords1
            
            # Angle needs to be rounded to use as a key for direction
            angle = np.round(np.arctan2(vector[1], vector[0]) * 180 / np.pi) * -1
            direction = [directions[key] for key in directions if angle in key][0]
            
            data = {"x": f"{(coords1[0] + coords2[0]) / 2}", "y": f"{(coords1[1] + coords2[1]) / 2}", "dir": direction}
            data = json.dumps(data)
            self.client.publish(f"/bots/hardware/{carNumber}", data)
        except:
            print(f"Could not find all coords for car {carNumber}")


    def getImage(self, lower, upper, getCoords = False):
        succes, img = self.cam.read()
        # img = cv2.imread(path)
        # img = cv2.resize(img, (640, 480))

        # img = self.transformPerspective(img)

        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        imgHSV = self.applySaturationAjustment(imgHSV)

        imgMasked = cv2.inRange(imgHSV, lower, upper)
        output = cv2.bitwise_and(img, img, mask = imgMasked)

        contour = cv2.findContours(imgMasked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = contour[0] if len(contour) == 2 else contour[1]
        
        for c in contour:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            if area > 300:
                # print(area)
                pass
            cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if getCoords:
                return np.array([x + 0.5 * w, y + 0.5 * h])
                
        return img, output
    
    def transformPerspective(self, img):
        cornersMaze = np.float32([upperLeft, upperRight, lowerLeft, lowerRight])
        cornersCam = np.float32([[0, 0], [mazeWidth, 0], [0, mazeHeight], [mazeWidth, mazeHeight]])
        matrix = cv2.getPerspectiveTransform(cornersMaze, cornersCam)

        return cv2.warpPerspective(img, matrix, (outputWindowWidth, outputWindowHeight))
    
    def applySaturationAjustment(self, img):
        # sat = img[..., 1]
        # sat = cv2.multiply(sat, self.satAdjustment)
        
        img[..., 1] = img[..., 1] * self.satAdjustment
        img[..., 2] = img[..., 2] * self.valAdjustment
        return img

    def mouseEvent(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONUP:
            print(x, y)

    ### MQTT functions
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        client.subscribe("/camera/coordinates")
        
        print("Subbed to topics")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        print("Message received in topic: " + topic)

        m_decode = int(msg.payload.decode("utf-8","ignore"))
        print("Data received", m_decode)

        self.getCoordinates(m_decode)

    
        

c = Camera()
# while 1:
#     pass
# c.calibrateColors()
c.run()
# c.calibrateColorAdjustment()
# c.getMazeCorners()