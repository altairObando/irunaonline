from django.contrib import admin
from .models import Job, JobSkill,Skill, Item, Monster, MonsterDrops
# Register your models here.


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    job = 'skillParent_name'
    list_filter = ('skillParent__Job__name','level')
    list_display = ('skillParent','name', 'level')
    search_fields = ('name',)
    ordering = ["level"]

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("name","desc")

@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_filter = ("Job", )
    list_display = ('Job','name','subSkills')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    search_fields = ('name','desc')
    list_display = ('name','desc','type',)

@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    list_display = ('name','imgSrc', 'attr')
@admin.register(MonsterDrops)
class DropsAdmin(admin.ModelAdmin):
    search_fields = ('baseItem__name',)
    list_display=('baseMonster', 'baseItem')