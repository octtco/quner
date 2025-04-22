from app.utils import getPublicData
from app.models import TravelInfo, NewComment

import json

travelInfoList = getPublicData.get_travel_info_data()
commentsList = getPublicData.get_comment_data()

def getSpotById(id):
    spot = TravelInfo.objects.get(id=id)
    spot.img_list = json.loads(spot.img_list)
    spot.comments = json.loads(spot.comments)
    return spot

def getNewCommentByName(name):
    # 预期返回多个对象，使用 filter() 并遍历结果：
    newComment = NewComment.objects.filter(travelTittle=name)
    return newComment
