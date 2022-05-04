from django.db import models
from django.contrib import admin
# Create your models here.
class Item(models.Model):
    pass

class Job(models.Model):
    name = models.CharField(max_length=150)
    desc = models.TextField(blank=True,null=True)
    def __str__(self):
        return self.name

class JobSkill(models.Model):
    Job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skillCode = models.CharField(verbose_name="Skill Code", max_length=150)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=250,null=True,blank=True)
    def __str__(self):
        return self.name
    @admin.display
    def subSkills(self):
        sub = Skill.objects.filter(skillParent=self)
        if sub is None or len(sub) <=0:
            return "sin falla"
        s=","
        return s.join(list(map(lambda item: item.name, list(sub))))



class Skill(models.Model):
    skillParent = models.ForeignKey(JobSkill, on_delete=models.CASCADE, verbose_name="Skill")
    ref = models.CharField(max_length=150,null=True,blank=True)
    level = models.CharField(max_length=150,null=True,blank=True)
    name  = models.CharField(max_length=150)
    item  = models.CharField(max_length=150,null=True,blank=True)
    itemRef = models.CharField(max_length=250,null=True,blank=True)

    