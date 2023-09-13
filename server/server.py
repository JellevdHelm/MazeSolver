import json
import mqtt as m
import pathplanner as pp
import robot as bot
import time
import threading

from typing import List
# Global variables
startSwarm = False

robots: List[bot.Robot] = []
bot0 = bot.Robot(0)
bot1 = bot.Robot(1)
bot2 = bot.Robot(2)
bot3 = bot.Robot(3)
robots.append(bot0)
robots.append(bot1)
robots.append(bot2)
robots.append(bot3)

pathPlanner = pp.PathPlanner(robots)
# grid = pathPlanner.mapCells(10)

noOfSimulatedBots = 2
noOfHardwareBots = 2

subTopicHard = "/bots/hardware/{}"
subTopicSoft = "/bots/software/{}"
subTopicStart = "/swarm/start"
pubTopicHard = "/bots/hardware/path/{}"
pubTopicSoft = "/bots/software/path/{}"
pubTopicStart = "/bots/hardware/start"


def sendAll(message):
    for i in range(noOfSimulatedBots):
        client.publish(pubTopicSoft.format(i), message)
        print(pubTopicSoft.format(i))
        print(message)
        time.sleep(1)
    for i in range(noOfHardwareBots):
        client.publish(pubTopicHard.format(i), message)
        print(pubTopicHard.format(i))
        print(message)
        time.sleep(1)


def worker(event):
    while True:
        time.sleep(2)
        sendAll("pos") # updates position x, y and dir (up, down, left, right)
        time.sleep(2)
        sendAll("check") #checks walls left front right
        #send direction to bot
        #send forward if bladibla
        time.sleep(5)
        
        print("bot0 position: ", bot0.position)
        print("bot0 direction: ", bot0.facingDirection)
        print("bot0 walls: ", bot0.sensorWall)
        
        print("bot1 position: ", bot1.position)
        print("bot1 direction: ", bot1.facingDirection)
        print("bot1 walls: ", bot1.sensorWall)
        
        print("bot2 position: ", bot2.position)
        print("bot2 direction: ", bot2.facingDirection)
        print("bot2 walls: ", bot2.sensorWall)
        
        print("bot3 position: ", bot3.position)
        print("bot3 direction: ", bot3.facingDirection)
        print("bot3 walls: ", bot3.sensorWall)
        
        pathPlanner.finalLoc(robots)
        
        for i in range(noOfSimulatedBots):
            print("forward to ", robots[i].nextDirection, " for bot ", i)
            if(robots[i].nextDirection != None):
                client.publish(pubTopicSoft.format(i), robots[i].nextDirection)
                time.sleep(2)
                client.publish(pubTopicSoft.format(i), "forward")
                robots[i].nextDirection = None
            time.sleep(1)
        for i in range(noOfHardwareBots):
            print("forward to ", robots[i+2].nextDirection, " for bot ", i+2)
            if(robots[i+2].nextDirection != None):
                client.publish(pubTopicHard.format(i), robots[i+2].nextDirection)
                time.sleep(2)
                client.publish(pubTopicHard.format(i), "forward")
                robots[i+2].nextDirection = None
            time.sleep(1)
        
        
        time.sleep(5)
        #event.wait()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    for i in range(noOfHardwareBots):
        client.subscribe(subTopicHard.format(i))
    for i in range(noOfSimulatedBots):
        client.subscribe(subTopicSoft.format(i))
    client.subscribe(subTopicStart)

    print("Subbed to topics")

# Callback function when receiving a message
def on_message(client, userdata, msg):
    topic = str(msg.topic)
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    # pause.clear()  # pause loop thread

    print("Message received in topic: " + topic)
    print("Message: ", m_decode)

    if topic == subTopicStart:
        print("boo")
        # time.sleep(0.5)
        # sendAll("pos")
        # time.sleep(1)
        # sendAll("check")
        updateThread.start()
    elif "hardware" in topic:
        if "dir" in m_decode:
            index = int(topic[-1])+noOfSimulatedBots
            pos = json.loads(m_decode)
            print("hardwaredir")
            print(pos)
            print(pos["x"])
            print(pos["y"])
            print(type(pos))
            robots[index].updatePosition(pos)
        elif "left" in m_decode:
            index = int(topic[-1])+noOfSimulatedBots
            dist = json.loads(m_decode)
            left = True
            front = True
            right = True
            print("hardwarewall")
            
                        
            if(dist["left"]<1000):
                left = False
            
            if(dist["front"]<1000):
                front = False
                
            if(dist["right"]<1000):
                right = False
                
            robots[index].updateWalls(left, front, right)
    elif "software" in topic:
        if "dir" in m_decode:
            index = int(topic[-1])
            pos = json.loads(m_decode)
            print("softwaredir")
            print(pos)
            print(pos["x"])
            print(pos["y"])
            print(type(pos))
            robots[index].updatePosition(pos)
        elif "left" in m_decode:
            index = int(topic[-1])
            dist = json.loads(m_decode)
            left = True
            front = True
            right = True
            print("softwarewall")
                        
            if(dist["left"]<1000):
                left = False
            
            if(dist["front"]<1000):
                front = False
                
            if(dist["right"]<1000):
                right = False
                
            robots[index].updateWalls(left, front, right)

    # pause.set() do this while sending messages back

    # pathPlanner.doUpdate()


if __name__ == "__main__":
    client = m.Mqtt("server", on_connect, on_message)
    client.connectMQTT()
    pause = threading.Event()
    updateThread = threading.Thread(target=worker, args=(pause,))

    while(1):
        pass #poo