from django.http import HttpResponse
from django.shortcuts import render, redirect
from app.models import User, TravelInfo
from django.db.models import Count, F, Q
from app.utils import getPublicData, getHomeData, getCommentsData, addComments



# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'base_login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            User.objects.get(username=username, password=password)
            request.session['username'] = username
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
            return redirect('/app/dashboard')
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
    newcomments = []
    newcomments = getCommentsData.getNewCommentByName(travelInfo.title)
    # showcomment = travelInfo.newComments

    if request.method == 'POST':
        addComments.addComments({
            'content': request.POST.get('content'),
            'userInfo': userInfo,
            'travelInfo': travelInfo,
        })
        return redirect(f'/app/addcomments/{id}')

    return render(request,'app/addcomments.html', {
        'userInfo': userInfo,
        'travelInfo':travelInfo,
        'id':id,
        'newcomments': newcomments
    })
