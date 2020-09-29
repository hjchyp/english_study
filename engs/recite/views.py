from django.shortcuts import render
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect,reverse
import json
from django.http import HttpResponse
from utils.mixin import LoginRequiredMixin,trans_excel_to_list
from django.conf import settings
import xlrd
import os
from recite.models import ItemBank,User,Learned,Test
import re
import random
from django.db.models import Max,Min
import datetime



# Create your views here.
class LoginView(View):
    '''登录界面'''
    def get(self,request):
        return render(request,
                      'login.html')
    def post(self,request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        # print(username)
        # print(password)
        user = authenticate(username=username,password=password)
        # print(user)
        # 先看看密码对不对
        if user is not None:
            login(request, user)
            return redirect(reverse('recite:menu'))
        else:
            errmsg = '用户名或密码错误'
            return render(request, 'login.html', context={'errmsg':errmsg})

class Learning(LoginRequiredMixin,View):
    def get(self,request):
        user_id = User.objects.get(username__exact=request.user).id
        eng_words, post_flag = learned_logic(user_id)

        return render(request,'words_recite.html',{'eng_words':eng_words,
                                                   'post_flag':post_flag})

    def post(self,request):

        user = User.objects.get(username__exact=request.user)

        remember_list = request.POST.get('remember_list')

        if remember_list == '':
            return redirect(reverse('recite:learning'))
        # print(remember_list)
        remember_list = remember_list.split(',')

        for i in remember_list:
            item_bank = ItemBank.objects.get(pk=i)
            obj = Learned.objects.create(item=item_bank,user=user,reviewed_times=0,test_times=0)
            obj.save()

        return redirect(reverse('recite:learning'))

class Menu(LoginRequiredMixin,View):
    def get(self,request):
        return render(request,'menu.html')

class Reviewing(LoginRequiredMixin,View):
    def get(self,request):
        user_id = User.objects.get(username__exact=request.user).id
        eng_words = review_logic(user_id)
        return render(request, 'words_reviewing.html', {'eng_words': eng_words})

    def post(self,request):
        user = User.objects.get(username__exact=request.user)
        answer_words = []
        for i in request.POST:
            if i.endswith('ans'):
                item_num = i[:-3]
                stu_answer = request.POST[i]
                item_bank = ItemBank.objects.get(pk=item_num)
                cor_answer = item_bank.item_en
                item_text = item_bank.item_ch
                ############ 修改learned表中的review, correct和incorrect次数
                reviewed_obj = Learned.objects.filter(item_id=item_num).get(user_id=user.id)
                if stu_answer == cor_answer:
                    is_correct = 1
                    reviewed_obj.correct_times += 1
                    reviewed_obj.incorrect_times += 0
                else:
                    is_correct = 0
                    reviewed_obj.correct_times += 0
                    reviewed_obj.incorrect_times += 1
                reviewed_obj.reviewed_times += 1
                reviewed_obj.save()

                answer_words.append([item_num,item_text,cor_answer,stu_answer,is_correct])
                test_object = Test.objects.create(item=item_bank,
                                                  user=user,
                                                  stu_answer=stu_answer,
                                                  is_correct=is_correct)
                test_object.save()
        return render(request, 'words_reviewing.html', {'answer_words':answer_words})

class LogoutView(LoginRequiredMixin,View):
    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)
        return redirect(reverse('recite:login'))


'''
学习的逻辑是（get方法）：
１．先学没有学过的
２．如果全学过了则在learned表中找到review次数最少的进行复习或者错误次数最多前２０个学习（随机）
'''
def learned_logic(user_id):

    # 查找单个学生学过的题库编号
    learned_list = [i.item_id for i in Learned.objects.filter(user_id=user_id)]

    # 把这个学生没学过的单词找出来返回到learning页面上
    sets = ItemBank.objects.exclude(item_id__in=learned_list)[:20]
    if len(sets) != 0:
        eng_words = [re.split(r'\s|=', str(i)) for i in sets]  # [1,chinese,eng1]
        post_flag = 1
        return eng_words,post_flag
    else:
        random_num = random.randint(1,2)
        post_flag = 0
        if random_num == 1:
            # 找到这个学生错误复习次数最少的数字
            minReviewed = Learned.objects.filter(user_id=user_id).aggregate(Min('reviewed_times'))
            # 从这个学生的数据中选取满足条件的对象
            min_sets = Learned.objects.filter(user_id=user_id).filter(reviewed_times=minReviewed['reviewed_times__min'])
            min_sets = [i.item_id for i in min_sets]
            min_sets = ItemBank.objects.filter(item_id__in=random_sample(min_sets,10))
            eng_words = [re.split(r'\s|=', str(i)) for i in min_sets]  # [1,chinese,eng1]

        else:
            maxIncorrect = Learned.objects.filter(user_id=user_id).aggregate(Max('incorrect_times'))
            max_sets = Learned.objects.filter(user_id=user_id).filter(incorrect_times=maxIncorrect['incorrect_times__max'])
            max_sets = [i.item_id for i in max_sets]
            max_sets = ItemBank.objects.filter(item_id__in=random_sample(max_sets,10))
            eng_words = [re.split(r'\s|=', str(i)) for i in max_sets]  # [1,chinese,eng1]

        return eng_words,post_flag

def random_sample(alist,num):
    '''
    数字列表随机抽取
    :param alist:
    :param num:
    :return:
    '''
    if len(alist) < num:
        num = len(alist)
    return random.sample(alist,num)


'''
复习逻辑：
１．先找ｌｅａｒｎｅｄ表里面reviewed_times次数最小的(且上次复习时间超过８个小时的)，不超过三
２．都ｒｅｖｉｅｗ，３遍后后则找correct_times次数最小的，不超过三
３．最后找错误率最高的
'''
def review_logic(user_id):


    now = datetime.datetime.now()

    minReviewed = Learned.objects.filter(user_id=user_id).aggregate(Min('reviewed_times'))
    # print(minReviewed)
    # 如果没学词语直接返回空
    if minReviewed['reviewed_times__min'] == None:
        eng_words = []
        return eng_words
    minCorrect = Learned.objects.filter(user_id=user_id).aggregate(Min('correct_times'))
    # 如果学了，那就先找复习次数最小的,根据复习的过的次数和时间进行筛选
    if minReviewed['reviewed_times__min'] < 3:
        # print(minReviewed)
        if minReviewed['reviewed_times__min'] < 1:
            min_sets = Learned.objects.filter(user_id=user_id).filter(
                reviewed_times=minReviewed['reviewed_times__min'])
        elif  minReviewed['reviewed_times__min'] == 1:
            min_sets = Learned.objects.filter(user_id=user_id).filter(
                reviewed_times=minReviewed['reviewed_times__min']).filter(
                update_time__lt=now-datetime.timedelta(minutes=15))
        elif minReviewed['reviewed_times__min'] == 2:
            min_sets = Learned.objects.filter(user_id=user_id).filter(
                reviewed_times=minReviewed['reviewed_times__min']).filter(
                update_time__lt=now - datetime.timedelta(hours=3))
        else:
            min_sets = Learned.objects.filter(user_id=user_id).filter(
                reviewed_times=minReviewed['reviewed_times__min']).filter(
                update_time__lt=now - datetime.timedelta(hours=8))
        min_sets = [i.item_id for i in min_sets]
        min_sets = ItemBank.objects.filter(item_id__in=random_sample(min_sets, 10))
        eng_words = [re.split(r'\s|=', str(i)) for i in min_sets]  # [1,chinese,eng1]

    elif minCorrect['correct_times__min'] < 1:
        # print(minCorrect)
        min_sets = Learned.objects.filter(user_id=user_id).filter(correct_times=minCorrect['correct_times__min'])
        min_sets = [i.item_id for i in min_sets]
        min_sets = ItemBank.objects.filter(item_id__in=random_sample(min_sets, 10))
        eng_words = [re.split(r'\s|=', str(i)) for i in min_sets]  # [1,chinese,eng1]

    else:
        # print(user_id)
        learned_list_3 = [i[0] for i in Learned.objects.get_incorrect_rate(user_id)]
        # print(learned_list_3)
        sets = ItemBank.objects.filter(item_id__in=learned_list_3)
        # print(sets)
        eng_words = [re.split(r'\s|=', str(i)) for i in sets]  # [1,chinese,eng1]

    return eng_words