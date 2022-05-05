from statistics import mode
from turtle import back
from django.db import models
from django.contrib import admin
# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True,verbose_name="Description")
    uri = models.TextField(blank=True,null=True)
    type= models.CharField(max_length=100,blank=True,null=True, verbose_name="Item Type") ## Recovery,Item,Sword,etc..
    zone=models.CharField(max_length=100,null=True  )
    def __string__(self):
        return self.name

class Monster(models.Model):
    name = models.CharField(max_length=200)
    imgSrc = models.TextField(blank=True,null=True)
    attr =models.CharField(max_length=50,null=True)
    weak =models.CharField(max_length=50,null=True)
    #img = models.ImageField(verbose_name="Image")

class MonsterDrops(models.Model):
    baseMonster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    baseItem    = models.ForeignKey(Item,on_delete=models.CASCADE)

class BlackSmithFormula(models.Model):
    itemResult = models.ForeignKey(Item, models.CASCADE)
    city = models.CharField(max_length=150, null=True)

class BlacksmithMaterials(models.Model):
    formula = models.ForeignKey(BlackSmithFormula, models.CASCADE)
    baseItem= models.ForeignKey(Item, models.CASCADE)
    quantity= models.IntegerField(null=True)

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

    