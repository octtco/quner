from django.db import models


# Create your models here.
def default_json_list():
    return []


class TravelInfo(models.Model):
    id = models.AutoField('id', primary_key=True)
    title = models.CharField('景区名', max_length=255, default='')
    level = models.CharField('等级', max_length=255, default='')
    discount = models.CharField('折扣', max_length=255, default='')
    saleCount = models.CharField('销量', max_length=255, default='')
    province = models.CharField('省份', max_length=255, default='')
    star = models.CharField('热度', max_length=255, default='')
    detailAddress = models.CharField('景点详情地址', max_length=255, default='')
    shortIntro = models.CharField('短评', max_length=255, default='')
    detailUrl = models.CharField('详情地址', max_length=255, default='')
    score = models.CharField('评分', max_length=255, default='')
    price = models.CharField('价格', max_length=255, default='')
    commentsLen = models.CharField('评论个数', max_length=255, default='')
    detailIntro = models.CharField('详情介绍', max_length=2555, default='')
    img_list = models.CharField('图片列表', max_length=2550, default='')
    comments = models.TextField('用户评论', default='')
    cover = models.CharField('封面', max_length=2555, default='')
    createTime = models.DateField('爬取时间', auto_now_add=True)
    # newComments = models.JSONField('添加用户评论',default=default_json_list)


class User(models.Model):
    id = models.AutoField('id', primary_key=True)
    username = models.CharField('用户名', max_length=255, default='')
    password = models.CharField('密码', max_length=255, default='')
    sex = models.CharField('性别', max_length=255, default='')
    address = models.CharField('地址', max_length=255, default='')
    avatar = models.FileField('头像', upload_to='avatar', default='avatar/default.png')
    textarea = models.CharField('个人简介', max_length=255, default='这个人很懒，什么有没留下。')
    createTime = models.DateField('创建时间', auto_now_add=True)


class NewComment(models.Model):
    id = models.AutoField('id', primary_key=True)
    # travelId = models.IntegerField('travelid',default=0)
    travelTittle = models.CharField(max_length=255, default='')
    # username = models.CharField('用户名',max_length=255,default='')
    content = models.TextField('评论内容', max_length=255, default='')
    creatTime = models.TextField('评论时间', max_length=255, default='')
    # avatar = models.FileField('头像',upload_to='avatar',default='avatar/default.png')
    # rate = models.IntegerField('评分', max_length=255, default=5)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # 当User被删除时，关联的评论也删除
        null=True,  # 允许数据库存储空值
        blank=True,  # 允许表单不填写
        verbose_name='关联用户',
        related_name='comments'  # 反向查询时的名称（可选）
    )

class UserRating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='用户',
        related_name='ratings'
    )
    TravelSpot = models.ForeignKey(
        TravelInfo,
        on_delete=models.CASCADE,
        verbose_name='景区',
        related_name='ratings'
    )
    rate = models.IntegerField('评分', default=5)

    class Meta:
        unique_together = ('user', 'TravelSpot')  # 添加联合唯一约束


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='用户行为',
        related_name='logs'
    )
    session_key = models.CharField(max_length=40)  # Django会话的session_key
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)  # 登出时间为空表示未登出
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)