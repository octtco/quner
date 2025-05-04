from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# 引入 Django 的消息框架
from django.contrib import messages
# 引入 login_required 装饰器
from django.contrib.auth.decorators import login_required

from app.models import User, TravelInfo, Comments
from django.db.models import Count, F, Q, Avg
from app.utils import getPublicData, getHomeData, getCommentsData, addComments, getUserData, modifyUserData, getAnalysisData,getRecommendationData, getPriceData, getSalesData
from app.recommdation import getUser_ratings,user_bases_collaborative_filtering


# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'base_login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user=User.objects.get(username=username, password=password)
            request.session['username'] = username
            request.session['avatar'] = user.avatar.path
            return redirect('/app/dashboard')
        except:
            return render(request, 'base_login.html', {'error_message': '用户名或密码错误'})


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        conf = request.POST.get("confirm_password")
        try:
            User.objects.get(username=username)
        except:
            if password != conf:
                return render(request, 'register.html', {'error_message': '密码不一致'})
            User.objects.create(username=username, password=password)
            return render(request, 'base_login.html')
        return render(request, 'register.html', {'error_message': '用户名已存在'})


def dashboard(request):
    # 5A级景点数量
    count_5a = TravelInfo.objects.filter(level__contains='5A').count()
    # 评论最多的景区
    most_comments_spot = TravelInfo.objects.order_by('-commentsLen').first()
    # 拥有景点最多的省份
    province_counts = TravelInfo.objects.values('province').annotate(count=Count('id')).order_by('-count')
    most_spots_province = province_counts.first()
    # 景点总数
    total_spots = TravelInfo.objects.count()
    # 评分排名前十的景区
    top_rated_spots = TravelInfo.objects.order_by('-score')[:10]
    # 评论数量排名前十的景区
    top_comments_spots = TravelInfo.objects.order_by('-commentsLen')[:10]
    # print(top_comments_spots.title)
    # 各省份景点数量
    province_spots_count = province_counts
    max_spots_province_count = province_counts.first()['count'] if province_counts else 0
    # 地理信息
    geoData = getHomeData.getGeoData()

    context = {
        'count_5a': count_5a,
        'most_comments_spot': most_comments_spot,
        'most_spots_province': most_spots_province,
        'total_spots': total_spots,
        'top_rated_spots': top_rated_spots,
        'top_comments_spots': top_comments_spots,
        'province_spots_count': province_spots_count,
        'max_spots_province_count': max_spots_province_count,
        "geoData": geoData
    }

    return render(request, 'app/dashboard.html', context)


def comments(request):
    all_spots = getPublicData.get_travel_info_data()

    context = {
        'all_spots': all_spots,
    }

    return render(request, 'app/comments.html', context)


def addcomments(request, id):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    travelInfo = getCommentsData.getSpotById(id)
    print(travelInfo.title)
    newcomments_list = getCommentsData.getNewCommentByName(travelInfo.title)
    
    # Pagination
    paginator = Paginator(newcomments_list, 5) # Show 5 comments per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        addComments.addComments({
            'content': request.POST.get('content'),
            'rate': int(request.POST.get('rate')),
            'userInfo': userInfo,
            'travelInfo': travelInfo,
        })
        return redirect(f'/app/addcomments/{id}')

    return render(request,'app/addcomments.html', {
        'userInfo': userInfo,
        'travelInfo': travelInfo,
        'id': id,
        'page_obj': page_obj  # Pass paginated comments to template
    })

# 城市与景点等级分析视图
def cityLevelAnalysis(request):
    cityList = []
    levelList = []
    cityData = getAnalysisData.getCityAnalysisData()
    levelData = getAnalysisData.getLevelAnalysisData()
    for city in cityData:
        cityList.append({"name": city["province"], "value": city["avg_score"]})
        print(cityList)

    for level in levelData:
        levelList.append({"name": level["level"],  "avg_score": level["avg_score"]})
        print(levelList)

    context = {
        # 'cityX': [c["province"] for c in cityList],
        # 'cityY': [c["count"] for c in cityList],
        # 'cityAVG': [c["avg_score"] for c in cityList],
        'levelY': [c["name"] for c in levelList],
        # 'levelX': [c["count"] for c in levelList],
        'levelAVG': [c["avg_score"] for c in levelList],
        'cityList': cityList,
        'levelList': levelList
    }
    print(context)
    return render(request, 'app/cityLevelAnalysis.html', context)


# 添加个人信息编辑视图
def personal_details(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    if request.method == 'POST':
        modifyUserData.modifyUserData(username, request.POST, request.FILES)
        userInfo = User.objects.get(username=username)

    return render(request, 'app/personaldetails.html', {
        'user': userInfo,
    })

# 价格分布分析视图
def priceAnalysis(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    cityList = getPublicData.getCityList()
    travelList = getPublicData.get_travel_info_data()
    xData, yData = getAnalysisData.getPriceAnalysisDataOne(travelList)
    x1Data, y1Data = getAnalysisData.getPriceAnalysisDataTwo(travelList)
    disCountPieData = getAnalysisData.getPriceAnalysisDataThree(travelList)
    return render(request, 'app/priceAnalysis.html', {
        'userInfo': userInfo,
        'cityList': cityList,
        'echartsData': {
            'xData': xData,
            'yData': yData,
            'x1Data': x1Data,
            'y1Data': y1Data,
            'disCountPieData': disCountPieData
        }
    })

# 销量分析视图

# 推荐视图
def recommendation(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    try:
        user_ratings = getUser_ratings()
        # print(user_ratings)
        recommended_items = user_bases_collaborative_filtering(userInfo.id, user_ratings)
        # print(userInfo.id)
        # print(recommended_items)
        resultDataList = getRecommendationData.getAllTravelByTitle(recommended_items)
        # print("recommendation1")
        # print(resultDataList)
    except:
        resultDataList = getRecommendationData.getRandomTravel()
        # print("recommendation2")
        # print(resultDataList)

    return render(request, 'app/recommendation.html', {
        'userInfo': userInfo,
        'resultDataList': resultDataList
    })
