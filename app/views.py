from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# 引入 Django 的消息框架
from django.contrib import messages
# 引入 login_required 装饰器
from django.contrib.auth.decorators import login_required

from app.models import User, TravelInfo, UserActivityLog
from django.db.models import Count, F, Q, Avg
from app.utils import getPublicData, getHomeData, getCommentsData, addComments, getUserData, modifyUserData, \
    getAnalysisData, getRecommendationData
from app.recommdation import *
from django.contrib.auth.signals import user_logged_in, user_logged_out
import datetime
from django.utils import timezone


# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'base_login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            # 明文验证（仅用于演示）
            user = User.objects.get(username=username, password=password)

            # 生成唯一会话ID（替代Django的session_key）
            custom_session_id = f"{timezone.now().timestamp()}-{user.id}"

            # 记录登录日志
            UserActivityLog.objects.create(
                user=user,
                session_key=custom_session_id,
                login_time=timezone.now(),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            # # 手动触发登录信号
            # user_logged_in.send(
            #     sender=User,
            #     request=request,
            #     user=user
            # )

            # 保存自定义会话信息
            request.session['username'] = username
            request.session['avatar'] = user.avatar.path
            request.session['custom_session_id'] = custom_session_id  # 关键配对标识
            return redirect('/app/dashboard')
        except:
            return render(request, 'base_login.html', {'error_message': '用户名或密码错误'})


def logout(request):
    # 获取当前会话信息
    session_id = request.session.get('custom_session_id')
    username = request.session.get('username')
    print("logout1")

    if username and session_id:
        try:
            print("logout")
            user = User.objects.get(username=username)
            # 更新登出时间
            log = UserActivityLog.objects.get(
                user=user,
                session_key=session_id,
                logout_time__isnull=True
            )
            log.logout_time = timezone.now()
            log.save()
            # # 手动触发登出信号
            # user_logged_out.send(
            #     sender=User,
            #     request=request,
            #     user=user
            # )
        except User.DoesNotExist:
            pass

    # 清除会话
    request.session.flush()
    return redirect('/app/login')  # 无论是否POST都跳转


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
    print(newcomments_list)
    # Pagination
    paginator = Paginator(newcomments_list, 5)  # Show 5 comments per page.
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

    return render(request, 'app/addcomments.html', {
        'userInfo': userInfo,
        'travelInfo': travelInfo,
        'id': id,
        'newcomments': newcomments_list,
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
        levelList.append({"name": level["level"], "avg_score": level["avg_score"]})
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
    print(userInfo)
    print(cityList)
    print(xData)
    print(yData)
    print(x1Data)
    print(y1Data)
    print(disCountPieData)
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


def userActivityAnalysis(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    date, hour, times, results = getAnalysisData.getUserActivityLogs(userInfo)
    print(date)
    print(hour)
    print(times)
    print(results)
    return render(request, 'app/userActivityAnalysis.html', {
        'date': date,
        'hour': hour,
        'times': times,
        'results': results
    })


# 推荐视图
def recommendation(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    try:

        # 1.加载数据
        # 系统数据
        user_ratings = getUser_ratings()
        # 网络数据
        olduser_ratings = getOldUser_ratings()

        # 2.构建混合用户画像
        hybrid_ratings = build_hybrid_user_ratings(user_ratings, olduser_ratings, w1=0.7, w2=0.3)

        # 3.计算用户相似度
        user_sim = compute_user_similarity(hybrid_ratings)

        # 4.生成推荐
        recommendations = hybrid_user_recommendation(
            target_user=userInfo.id,
            hybrid_ratings=hybrid_ratings,
            user_sim=user_sim,
            top_n=6
        )
        resultDataList = getRecommendationData.getAllTravelByTitle(recommendations)
    except:
        resultDataList = getRecommendationData.getRandomTravel()

    return render(request, 'app/recommendation.html', {
        'userInfo': userInfo,
        'resultDataList': resultDataList
    })
def detailIntroCloud(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    return render(request, 'app/detailIntroCloud.html', {
        'userInfo': userInfo,
    })

def commentContentCloud(request):
    username = request.session.get('username')
    userInfo = User.objects.get(username=username)
    return render(request, 'app/commentContentCloud.html', {
        'userInfo': userInfo,
    })
