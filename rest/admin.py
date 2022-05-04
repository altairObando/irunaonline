from django.contrib import admin
from .models import Job, JobSkill,Skill
# Register your models here.
admin.site.register(Job)
admin.site.register(JobSkill)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    job = 'skillParent_name'
    list_filter = ('skillParent__Job__name','level')
    list_display = ('skillParent','name', 'level')
    search_fields = ('name',)

