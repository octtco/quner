from app.models import UserActivityLog
from django.db.models import Count
from django.db.models.functions import TruncDate, ExtractHour

def calculateOnlineTime(user):
    logs = UserActivityLog.objects.filter(user=user).exclude(logout_time__isnull=True)
    total_seconds = sum(
        (log.logout_time - log.login_time).total_seconds()
        for log in logs
    )
    return total_seconds

def getUserActivityLogs(user):
    # 使用ORM查询生成数据
    clean_data = (
        UserActivityLog.objects.filter(user=user)
        .annotate(
            date=TruncDate('login_time'),  # 提取日期（YYYY-MM-DD）
            hour=ExtractHour('login_time')  # 提取小时（0-23）
        )
        .values('date', 'hour')  # 按日期和小时分组
        .annotate(count=Count('id'))  # 统计每个组的记录数
        .order_by('date', 'hour')  # 按日期和小时排序
    )
    date = []
    hour = []
    times = []
    # 转换为需要的列表格式
    results = [
        [log['date'].strftime('%Y-%m-%d'), log['hour'], log['count']]for log in clean_data
    ]
    for result in results:
        date.append(result[0])
        hour.append(result[1])
        times.append(result[2])
    return date, hour, times
