import robot as bot
import matplotlib.pyplot as plt
import numpy as np
import random

from enum import Enum

noOfSimulatedBots = 0
noOfHardwareBots = 2

### Path planning variables
sensorWall = np.array([False, True, False], dtype=bool) #Left, Front, Right
facingDirection = "North"
currX = 7
currY = 2
previousLocations = set()
#botPosition = np.array([4,5], dtype=int)

### Plotting variables
mid_x, mid_y = 5, 5
max_x, max_y = 11, 11 
min_x, min_y = 0, 0
step_size = 1
num_points = 10

### Visualize grid 
x_range = np.concatenate((np.arange(min_x, mid_x, step_size), np.arange(mid_x, max_x, step_size)))
y_range = np.concatenate((np.arange(min_y, mid_y, step_size), np.arange(mid_y, max_y, step_size)))

data = np.array([[x, y] for x in x_range for y in y_range])  # cartesian prod

# plt.scatter(data[:, 0], data[:, 1])
# plt.scatter(mid_x, mid_y, color='r')
# plt.show()

class Directions(Enum):
    NORTH = "up"
    EAST = "right"
    SOUTH = "down"
    WEST = "left"

class PathPlanner:        
    def __init__(self, bots):
        self.bots = bots 
        pass
    
    def mapGrid(self):

        pass

    def mapCells(self, num_points):

        cell_List = []

        for x in range (1,num_points+1):
            for y in range (1, num_points+1):

                cell = str(x) + str(y)

                cell_List.append(cell)
        
        #print(cell_List())

        return(cell_List)

    def currLoc(self, currX, currY):
        currLoc = np.array([currX, currY], dtype=int)
        return currLoc

    def nextLoc(self, facingDirection, sensorWall, currX, currY):

            left = sensorWall[0]
            front = sensorWall[1]
            right = sensorWall[2]

            availableX = currX
            availableY = currY

            #print(left,front,right) # 0 is left, 1 is front, 2 is right
            nextCoords = []
            nextDirection = []
            
            if(front == True): #False is wall, True is no wall
                if(facingDirection == Directions.NORTH.value):
                    # coordsY= np.append(coordsY, availableY+1)
                    nextCoords.append((availableX, availableY + 1))
                    nextDirection.append(Directions.NORTH.value)
                elif(facingDirection == Directions.SOUTH.value):
                    # coordsY = np.append(coordsY, availableY-1)
                    nextCoords.append((availableX, availableY - 1))
                    nextDirection.append(Directions.SOUTH.value)
                elif(facingDirection == Directions.EAST.value):
                    # coordsX = np.append(coordsX, availableX+1)
                    nextCoords.append((availableX + 1, availableY))
                    nextDirection.append(Directions.EAST.value)
                elif(facingDirection == Directions.WEST.value):
                    # coordsX = np.append(coordsX, availableX-1)
                    nextCoords.append((availableX - 1, availableY))
                    nextDirection.append(Directions.WEST.value)

            if(sensorWall == (False, True, False)): #DeadEnd by bot
                if(facingDirection == Directions.NORTH.value):
                    # coordsY= np.append(coordsY, availableY-1)
                    nextCoords.append((availableX, availableY - 1))
                    nextDirection.append(Directions.SOUTH.value)
                elif(facingDirection == Directions.SOUTH.value):
                    # coordsY = np.append(coordsY, availableY+1)
                    nextCoords.append((availableX, availableY + 1))
                    nextDirection.append(Directions.NORTH.value)
                elif(facingDirection == Directions.EAST.value):
                    # coordsX = np.append(coordsX, availableX-1)
                    nextCoords.append((availableX - 1, availableY))
                    nextDirection.append(Directions.WEST.value)
                elif(facingDirection == Directions.WEST.value):
                    # coordsX = np.append(coordsX, availableX+1)
                    nextCoords.append((availableX + 1, availableY))
                    nextDirection.append(Directions.EAST.value)
            
            if(left == True):
                if(facingDirection == Directions.NORTH.value):
                    # coordsX = np.append(coordsX, availableX-1)
                    nextCoords.append((availableX - 1, availableY))
                    nextDirection.append(Directions.WEST.value)
                elif(facingDirection == Directions.SOUTH.value):
                    # coordsX = np.append(coordsX, availableX+1)
                    nextCoords.append((availableX + 1, availableY))
                    nextDirection.append(Directions.EAST.value)
                elif(facingDirection == Directions.EAST.value):
                    # coordsY = np.append(coordsY, availableY+1)
                    nextCoords.append((availableX, availableY + 1))
                    nextDirection.append(Directions.NORTH.value)
                elif(facingDirection == Directions.WEST.value):
                    # coordsY = np.append(coordsY, availableY-1)
                    nextCoords.append((availableX, availableY - 1))
                    nextDirection.append(Directions.SOUTH.value)

            if(right == True):
                if(facingDirection == Directions.NORTH.value):
                    # coordsX = np.append(coordsX, availableX+1)
                    nextCoords.append((availableX + 1, availableY))
                    nextDirection.append(Directions.EAST.value)
                elif(facingDirection == Directions.SOUTH.value):
                    # coordsX = np.append(coordsX, availableX-1)
                    nextCoords.append((availableX - 1, availableY))
                    nextDirection.append(Directions.WEST.value)
                elif(facingDirection == Directions.EAST.value):
                    # coordsY = np.append(coordsY, availableY-1)
                    nextCoords.append((availableX, availableY - 1))
                    nextDirection.append(Directions.SOUTH.value)
                elif(facingDirection == Directions.WEST.value):
                    # coordsY = np.append(coordsY, availableY+1)
                    nextCoords.append((availableX, availableY + 1))
                    nextDirection.append(Directions.NORTH.value)

            if(sensorWall == (False, False, False)): #DeadEnd
                if(facingDirection == Directions.NORTH.value):
                    # coordsY= np.append(coordsY, availableY-1)
                    nextCoords.append((availableX, availableY - 1))
                    nextDirection.append(Directions.SOUTH.value)
                elif(facingDirection == Directions.SOUTH.value):
                    # coordsY = np.append(coordsY, availableY+1)
                    nextCoords.append((availableX, availableY + 1))
                    nextDirection.append(Directions.NORTH.value)
                elif(facingDirection == Directions.EAST.value):
                    # coordsX = np.append(coordsX, availableX-1)
                    nextCoords.append((availableX - 1, availableY))
                    nextDirection.append(Directions.WEST.value)
                elif(facingDirection == Directions.WEST.value):
                    # coordsX = np.append(coordsX, availableX+1)
                    nextCoords.append((availableX + 1, availableY))
                    nextDirection.append(Directions.EAST.value)
                
            #print("Current coords: ", currX, currY)
            #print("Available coords: ", nextCoords)
            # print(sensorWall)
            return nextCoords, nextDirection
        
    
    def finalLoc(self, bots):
        chosenLocations = set()
        currentBotLocations = set()
        for bot in bots:
            # print("<---- start findLoc method ---->")
            # print("This bot is facing direction: ", bot.facingDirection)

            availableOptions, nextDirections = self.nextLoc(bot.facingDirection, bot.sensorWall, bot.position[0], bot.position[1])
            
            for bot2 in bots:
                previousLocations.add(bot2.position)
                currentBotLocations.add(bot2.position)
                print(bot.position, "Length available options in for loop: ", len(availableOptions))
                print(bot.position, "Available coords: ", availableOptions)
                print(bot.position, "current bot locations: ", currentBotLocations)
                print(bot.position, "i.position value = ", bot2.position)
                if bot2.position in availableOptions:
                    optionIndex = availableOptions.index(bot2.position)
                    del availableOptions[optionIndex]
                    del nextDirections[optionIndex]

            for index, option in enumerate(availableOptions):
                # print("kijkhier")
                # print(option)
                # print(chosenLocations)
                if option in chosenLocations:
                    continue
                
               
                elif (len(availableOptions) >= 2 and option in previousLocations):
                    # If everything is a previous location, select one from all options (priority is front, random left or right))
                    if option == availableOptions[-1]:
                        for index2, dir in enumerate(nextDirections):
                            # priority is front
                            if dir == bot.facingDirection:
                                print(bot.position, "Prioritizing front")
                                location = availableOptions[index2]
                                chosenLocations.add(location)
                                bot.setNext(location, dir)
                                break
                            elif dir == nextDirections[-1]:
                                print(bot.position, "Choosing random locations")
                                randIndex = random.randint(0, len(availableOptions) - 1)
                                location = availableOptions[randIndex]
                                chosenLocations.add(location)
                                bot.setNext(location, dir)
                                
                    print("<------ elif statement length: ", len(availableOptions))
                    continue

                else:
                    chosenLocations.add(option)
                    bot.setNext(option, nextDirections[index])
                    print("Chosen location: ", chosenLocations)
                    break

    def prevLoc():
        pass
