from app.utils import getPublicData

travelInfoList = getPublicData.get_travel_info_data()
commentsList = getPublicData.get_comment_data()

def get_five_A_count():
    five_A_count = 0
    for travelInfo in travelInfoList:
        if travelInfo.level == '5A景区':
            five_A_count += 1
    return five_A_count

def get_comments_count():
    max_tittle = ''
    max_comments = 0
    for travelInfo in travelInfoList:
        if travelInfo.commentslen > max_comments:
            max_comments = travelInfo.comments.count()
            max_tittle = travelInfo.title
    return max_tittle, max_comments

def getGeoData():
    dataDic = {}
    for i in travelInfoList:
        for j in getPublicData.cityList:
            for city in j['city']:
                if city.find(i.province) != -1:
                    if dataDic.get(j['province'],-1) == -1:
                        dataDic[j['province']] = 1
                    else:
                        dataDic[j['province']] += 1

    resutData = []
    for key,value in dataDic.items():
        resutData.append({
            'name':key,
            'value':value
        })
    return resutData

