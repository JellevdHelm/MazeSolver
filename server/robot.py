class Robot:
    def __init__(self, speed):
        self.position = None
        # The turns made?
        self.nodes = []     
        self.nextLocation = ()
        self.nextDirection = None
        self.facingDirection = None
        self.sensorWall = []

    def updatePosition(self, pos):
        self.position = (pos["x"], pos["y"])
        self.facingDirection = pos["dir"]
        
    def updateWalls(self, left, front, right):
        self.sensorWall = (left, front, right)

    def setNext(self, location, direction):
        self.nextLocation = location
        self.nextDirection = direction