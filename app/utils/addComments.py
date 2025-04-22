import time
import json

from app.models import NewComment


def getNowTime():
    timeFormat = time.localtime()
    year = timeFormat.tm_year
    mon = timeFormat.tm_mon
    day = timeFormat.tm_mday
    return year,mon,day

def addComments(commentData):
    # 'author': author,
    # 'content': content,
    # 'date': date,
    # 'score': score
    # authorId
    year,month,day = getNowTime()
    travelInfo = commentData['travelInfo']
    NewComment.objects.create(travelTittle=travelInfo.title,
                              username=commentData['userInfo'].username,
                              content=commentData['content'],
                              creatTime=str(year) + '-' + str(month) + '-' + str(day))
    # travelInfo.newComments.append({
    #     'author':commentData['userInfo'].username,
    #     # 'score':commentData['rate'],
    #     'content':commentData['content'],
    #     'date':str(year) + '-' + str(month) + '-' + str(day),
    #     # 'userId':commentData['userInfo'].id,
    # })
    travelInfo.comments = json.dumps(travelInfo.comments)
    travelInfo.img_list = json.dumps(travelInfo.img_list)
    travelInfo.save()