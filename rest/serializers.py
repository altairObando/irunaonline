from rest_framework import serializers
from .models import Item, Job, Skill,MonsterDrops

class DropSerializer(serializers.ModelSerializer):
    baseMonster = serializers.SlugRelatedField(many=False,read_only=True, slug_field="name")
    baseItem = serializers.SlugRelatedField(many=False,read_only=True, slug_field="name")
    class Meta:
        model=MonsterDrops
        fields =["id","baseMonster","baseItem"]
class ItemSerializer(serializers.ModelSerializer):
    monsterdrops_set = DropSerializer(many=True, read_only=True)
    class Meta:
        model = Item
        fields = ["id","name","desc","imageAlt","imgSrc","uri","type","atk","deff","notes","monsterdrops_set" ]

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'