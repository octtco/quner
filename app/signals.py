from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from app.models import UserActivityLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # 获取会话ID和客户端信息
    session_key = request.session.session_key
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # 创建登录记录
    UserActivityLog.objects.create(
        user=user,
        session_key=session_key,
        ip_address=ip_address,
        user_agent=user_agent
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # 确保用户已认证且会话存在
    if user and hasattr(request, 'session') and request.session.session_key:
        session_key = request.session.session_key
        try:
            # 查找未登出的记录
            log = UserActivityLog.objects.get(
                user=user,
                session_key=session_key,
                logout_time__isnull=True
            )
            log.logout_time = timezone.now()
            log.save()
        except UserActivityLog.DoesNotExist:
            # 处理异常情况（如重复登出）
            pass