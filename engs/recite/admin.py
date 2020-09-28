from django.contrib import admin
from recite.models import User,ItemBank,Unit,Learned,Test
# Register your models here.



class ItemBankInfo(admin.ModelAdmin):
    list_display = ['item_en','item_ch']
    model = ItemBank

class UserInfo(admin.ModelAdmin):
    list_display = ['username']
    model = User

class UnitInfo(admin.ModelAdmin):
    list_display = ['unit_name']
    model = Unit

class LearnedInfo(admin.ModelAdmin):
    list_display = ['user_id']
    model = Learned

class TestInfo(admin.ModelAdmin):
    list_display = ['user_id']
    model = Test

admin.site.register(ItemBank, ItemBankInfo)
admin.site.register(User, UserInfo)
admin.site.register(Unit, UnitInfo)
admin.site.register(Learned, LearnedInfo)
admin.site.register(Test, TestInfo)