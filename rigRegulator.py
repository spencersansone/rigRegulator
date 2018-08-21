import requests
import json
import datetime
from pyHS100 import SmartPlug
from time import sleep

#Enter tplink power switch ips here

#Example Format:

#POWER_SWITCH_IP_DICT = dict(
    #RIG_NAME="ENTER RIG IP ADDRESS HERE",
    #ANOTHER_RIG_NAME="ANOTHER RIG IP ADDRESS HERE",
    #...
    #...
    #...)

POWER_SWITCH_IP_DICT = dict(
    smr1="192.168.1.101",
    cj1="192.168.1.102")

RIG_SPEED_MINIMUM = dict(
    smr1=1200,
    cj1=1600)

def getMachinesLeftToCheck():
    outputArray = []
    for a,b in POWER_SWITCH_IP_DICT.items():
        outputArray += [a]
    return outputArray

def cyclePower(rigName):
    if rigName in POWER_SWITCH_IP_DICT:
        plug = SmartPlug(POWER_SWITCH_IP_DICT[rigName])
        plug.turn_off()
        sleep(2)
        plug.turn_on()

def getApiData():
    while(True):
        try:
            url = "https://api.nanopool.org/v1/zec/user/t1TKr7vXiXYxm9UxD1pUbYWy3pJPrvmuFDm"
            print("Attempt to grab API data...")
            apiData = json.loads(requests.get(url).text)
            print("Done!")
            return apiData
        except:
            pass

while(True):
    machines_left_to_check = getMachinesLeftToCheck()

    apiData = getApiData()

    print("Grabbing Vars...")
    currentDatetime = datetime.datetime.today()
    currentDate = currentDatetime.date()
    currentTime = currentDatetime.time()
    
    totalHashrate = apiData['data']['hashrate']
    workersInfo = apiData['data']['workers']

    print("Done!")
    rigHashrates = ""
    
    for worker in workersInfo:
        worker_id = worker['id']
        worker_hashrate = float(worker['hashrate'])
        min_speed = RIG_SPEED_MINIMUM[worker_id]

        rigHashrates += "\t{} : {}\n".format(
            worker_id,
            worker_hashrate)
        
        if worker_hashrate == 0 or worker_hashrate < min_speed:
            cyclePower(worker_id)
            rigHashrates += "\t\tStatus: RESTARTED\n"
        else:
            rigHashrates += "\t\tStatus: Normal\n"
            
        machines_left_to_check.remove(worker_id)

    message = """
******************************

Date: {}
Time: {}

Total Hashrate: {}

Rig Hashrates:
{}""".format(currentDate,currentTime, totalHashrate, rigHashrates)

    print(message)
    print("Outages:")
    if len(machines_left_to_check) == 0:
        print("No outages detected!")
        
    for machine in machines_left_to_check:
        print("\t{} IS DOWN...".format(machine))
        cyclePower(machine)
        print("\tRESTARTED!\n")
    print("******************************")
    sleep(15*60)
