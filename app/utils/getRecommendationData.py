from app.utils.getPublicData import get_travel_info_data
import random


def getAllTravelByTitle(traveTitleList):
    resultList = []
    for title in traveTitleList:
        for travel in get_travel_info_data():
            if title == travel.title: resultList.append(travel)
    return resultList


def getRandomTravel():
    travelList = get_travel_info_data()
    maxLen = len(travelList)
    resultList = []
    for i in range(6):
        randomNum = random.randint(0, maxLen)
        resultList.append(travelList[randomNum])
    return resultList
