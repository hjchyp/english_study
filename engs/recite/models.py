from django.db import models,connection
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
from django.conf import settings

TEST_TYPE_CHOICES = ((1, '复习'),
                     (2,'测验'))

IS_CORRECT = ((0,'错误'),
              (1,'正确'))

ITEM_TYPE_CHOICES = ((1,'汉英'),
                     (2,'英汉'),
                     (3,'汉英句子'),
                     (4,'英汉句子'))

class PersonManager(models.Manager):
    def get_incorrect_rate(self,user_id):
        cursor = connection.cursor()
        sql = '''select item_id, round(incorrect_times/reviewed_times*100,1) incorrect_rate from df_learned
                where user_id = %s and TIMEDIFF(now(),update_time) > '08:10:00'
                ORDER BY incorrect_rate DESC
                limit 20
                '''
        # print('qqqq',user_id)
        cursor.execute(sql,user_id)
        res = cursor.fetchall()
        return res


# Create your models here.
class User(AbstractUser, BaseModel):
    '''用户模型类'''
    # def authenticate(self,request=None,username=None,password=None,**kwargs):
    #     print(kwargs)
    #     print(**kwargs)
    #     user = User.objects.get(username=username)
    #     print('赵饶了',user)
    #     return user
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     if username is None:
    #         username = kwargs.get(User)
    #     try:
    #         user = User._default_manager.get_by_natural_key(username)
    #     except User.DoesNotExist:
    #         # Run the default password hasher once to reduce the timing
    #         # difference between an existing and a nonexistent user (#20760).
    #         User().set_password(password)
    #     else:
    #         print(username, 'internal')
    #         print(user, 'internal')
    #         print(user.check_password(989))
    #         print(self.user_can_authenticate(user))
    #         print(password,'password')
    #         if user.check_password(password) and self.user_can_authenticate(user):
    #             return user
    #
    # def user_can_authenticate(self, user):
    #     """
    #     Reject users with is_active=False. Custom user models that don't have
    #     that attribute are allowed.
    #     """
    #     is_active = getattr(user, 'is_active', None)
    #     return is_active or is_active is None

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class ItemBank(BaseModel):
    '''题库'''
    item_id = models.AutoField(primary_key=True,verbose_name='题目编号')
    item_ch = models.TextField(max_length=2560,verbose_name='题目中文')
    item_en = models.TextField(max_length=2560,verbose_name='题目英文')
    unit = models.ForeignKey('recite.Unit',verbose_name='单元',on_delete=models.CASCADE) # 外键
    version_num = models.IntegerField(verbose_name='题目版本',default=1)
    item_type = models.IntegerField(choices=ITEM_TYPE_CHOICES,verbose_name='题目类型',default=1)
    unit_item_id = models.IntegerField(verbose_name='单元题目编号',default=None)

    def __str__(self):
        return '%s=%s=%s' % (self.item_id ,self.item_ch,self.item_en)

    class Meta:
        db_table = 'df_item_bank'
        verbose_name = '题库'
        verbose_name_plural = verbose_name

class Unit(BaseModel):
    '''单元表'''
    unit_id = models.AutoField(verbose_name='单元id',primary_key=True)
    unit_name = models.CharField(max_length=128,verbose_name='单元名称')

    class Meta:
        db_table = 'df_unit'
        verbose_name = '单元表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.unit_name

class Learned(BaseModel):
    '''已学'''
    learned_id = models.AutoField(verbose_name='学习编号',primary_key=True)
    item = models.ForeignKey('recite.ItemBank',verbose_name='题目编号',on_delete=models.CASCADE)
    user = models.ForeignKey('recite.User',verbose_name='学生编号',on_delete=models.CASCADE)
    reviewed_times = models.IntegerField(verbose_name='复习次数')
    test_times = models.IntegerField(verbose_name='测验次数')
    incorrect_times = models.IntegerField(verbose_name='错误次数',default=0)
    correct_times = models.IntegerField(verbose_name='正确次数',default=0)
    objects = PersonManager()

    class Meta:
        db_table = 'df_learned'
        verbose_name = '已学表'
        verbose_name_plural = verbose_name



class Test(BaseModel):
    test_id = models.AutoField(verbose_name='测试编号',primary_key=True)
    item = models.ForeignKey('recite.ItemBank',verbose_name='题目编号',on_delete=models.CASCADE)
    user = models.ForeignKey('recite.User',verbose_name='学生编号',on_delete=models.CASCADE)
    test_type = models.SmallIntegerField(choices=TEST_TYPE_CHOICES, default=1, verbose_name='测试类型')
    stu_answer = models.TextField(max_length=2560,verbose_name='学生答案')
    is_correct = models.BooleanField(choices=IS_CORRECT)

    class Meta:
        db_table = 'df_test'
        verbose_name = '测试表'
        verbose_name_plural = verbose_name

class BookImage(BaseModel):
    pic_id = models.AutoField(verbose_name='书目编号',primary_key=True)
    image_name = models.CharField(max_length=128,verbose_name='书目名称')
    image_url = models.ImageField(upload_to='images/')