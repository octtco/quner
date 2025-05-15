from app.models import TravelInfo
from django.db.models import Count, Avg
from app.utils import getPublicData
from app.models import UserActivityLog
from django.db.models.functions import TruncDate, ExtractHour, ExtractDay


travelInfoList = getPublicData.get_travel_info_data()


def getCityAnalysisDataXY():
    cityDic = {}
    for travel in travelInfoList:
        if cityDic.get(travel.province, -1) == -1:
            cityDic[travel.province] = 1
        else:
            cityDic[travel.province] += 1

    return list(cityDic.keys()), list(cityDic.values())


def getCityAnalysisData():
    """获取城市和景点等级分析所需的数据。"""
    # 按省份分组统计景点数量和平均分
    city_analysis = TravelInfo.objects.values('province') \
        .annotate(count=Count('id'), avg_score=Avg('score')) \
        .order_by('-count')

    return city_analysis


def getLevelAnalysisData():
    # 按景点等级分组统计数量和平均分
    level_analysis = TravelInfo.objects.values('level') \
        .annotate(count=Count('id'), avg_score=Avg('score')) \
        .order_by('level')  # 或者根据需要排序，例如按等级排序

    return level_analysis


def getPriceAnalysisDataOne(traveList):
    xData = ['免费', '100元以内', '200元以内', '300元以内', '400元以内', '500元以内', '500元以上']
    yData = [0 for x in range(len(xData))]
    for travel in traveList:
        price = float(travel.price)
        if price <= 10:
            yData[0] += 1
        elif price <= 100:
            yData[1] += 1
        elif price <= 200:
            yData[2] += 1
        elif price <= 300:
            yData[3] += 1
        elif price <= 400:
            yData[4] += 1
        elif price <= 500:
            yData[5] += 1
        elif price > 500:
            yData[6] += 1
    return xData, yData


def getPriceAnalysisDataTwo(traveList):
    xData = [str(x * 300) + '份以内' for x in range(1, 15)]
    yData = [0 for x in range(len(xData))]
    for travel in traveList:
        saleCount = float(travel.saleCount)
        for x in range(1, 15):
            count = x * 300
            if saleCount <= count:
                yData[x - 1] += 1
                break

    return xData, yData


def getPriceAnalysisDataThree(travelList):
    startDic = {}
    for travel in travelList:
        if startDic.get(travel.discount, -1) == -1:
            startDic[travel.discount] = 1
        else:
            startDic[travel.discount] += 1
    resultData = []
    for key, value in startDic.items():
        resultData.append({
            'name': key,
            'value': value
        })
    return resultData

def getUserActivityLogs(user):

    # 使用ORM查询生成数据
    clean_data = (
        UserActivityLog.objects.filter(user=user)
        .annotate(
            day=ExtractDay('login_time'),  # 提取日期（YYYY-MM-DD）
            hour=ExtractHour('login_time')  # 提取小时（0-23）
        )
        .values('day', 'hour')  # 按日期和小时分组
        .annotate(count=Count('id'))  # 统计每个组的记录数
        .order_by('day', 'hour')  # 按日期和小时排序
    )

    # # 转换为需要的列表格式
    # date = []
    # hour = []
    # times = []
    # # 转换为需要的列表格式
    results = [
        [log['day'], log['hour'], log['count']] for log in clean_data
    ]
    print(results)
    # for result in results:
    #     date.append(result[0])
    #     hour.append(result[1])
    #     times.append(result[2])

    date = [log['day'] for log in clean_data]  # 示例：["5", "12", "28"]
    hour = [log['hour'] for log in clean_data]
    times = [log['count'] for log in clean_data]
    return date, hour, times, results
