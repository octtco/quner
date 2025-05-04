import time
import json

from app.models import NewComment, UserRating


def getNowTime():
    timeFormat = time.localtime()
    year = timeFormat.tm_year
    mon = timeFormat.tm_mon
    day = timeFormat.tm_mday
    return year, mon, day


def addComments(commentData):
    # 'author': author,
    # 'content': content,
    # 'date': date,
    # 'score': score
    # authorId
    year, month, day = getNowTime()
    print(type(commentData))
    travelInfo = commentData['travelInfo']
    NewComment.objects.create(travelTittle=travelInfo.title,
                              user=commentData['userInfo'],
                              content=commentData['content'],
                              creatTime=str(year) + '-' + str(month) + '-' + str(day))
    try:
        user_rating = UserRating.objects.get(user=commentData['userInfo'], TravelSpot=travelInfo)
    except:
        UserRating.objects.create(user=commentData['userInfo'],
                                  TravelSpot=travelInfo,
                                  rate=commentData['rate'])
        print("1")
    else:
        user_rating.rate = commentData['rate']
        user_rating.save()
        print("2")

    travelInfo.comments = json.dumps(travelInfo.comments)
    travelInfo.img_list = json.dumps(travelInfo.img_list)
    travelInfo.save()
