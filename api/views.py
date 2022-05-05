from ast import arg
from asyncio import subprocess
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
from .scrapper import Scrapper
from rest.models import Job, JobSkill, Skill, Item
from threading import Thread
from django.db import transaction
import time
# Create your views here.
api = Scrapper()

def index(_):
    return JsonResponse(api.GetPets(), safe=False)

def recoveryItems(_, section):
    return JsonResponse(api.GetRecoveryItems(section), safe=False)

def item(_, itemname):
    return JsonResponse(api.GetFullItem(itemname), safe=False)

def search(_, search):
    return JsonResponse(api.GetSearchResult(search), safe=False)

def skills(request,job):
    updateRecords = request.GET.get('update',False)
    requestSkill = api.GetSkills(job)
    
    if updateRecords == "true":
        updateSkills(job, requestSkill)

    return JsonResponse(requestSkill, safe=False)

def sync(_):
    ## Store scrap models
    ## Store Skills
    list_jobs = [
        "Adventurer",
        "Alchemist",
        "Assassin",
        "Beast Knight",
        "Bishop",
        "Cleric",
        "Enchanter",
        "Gladiator",
        "High Wizard",
        "Hunter",
        "Knight",
        "Mage",
        "Minstrel",
        "Monk",
        "Necromancer",
        "Ninja",
        "Paladin",
        "Samurai",
        "Servant",
        "Sniper",
        "Summoner",
        "Warrior",
        "Wizard",
    ]
    for job in list_jobs:
        try:
            thread = Thread(target=GetAndUpdateSkill,args=(job,))
            thread.start()
        except Exception as e:
            return JsonResponse({ "msg": "error saving " + job, "ex": e },safe=False)
    return JsonResponse({"msg": "Sync Jobs started"}, safe=False)


def GetAndUpdateSkill(jobname):
    info = api.GetSkills(jobname)
    updateSkills(jobname, info)

def updateSkills(job, requestSkill):
    #Recuperar el job
    dbJob = Job.objects.filter(name=job).first()
    if dbJob is None and len(requestSkill) <= 0:
        return JsonResponse({'error': True, 'msg': ('%s not found in db' % job)})
    if dbJob is None:
        dbJob = Job.objects.create(name=job, desc=job)
        dbJob.save()
    for skill in requestSkill:
        currentSkill = JobSkill.objects.filter(name=skill.get("name")).first()
        if currentSkill is None:
            currentSkill = JobSkill.objects.create(name=skill.get("name"),description=skill.get("description"),Job=dbJob )
            currentSkill.save()
        for newSubSkill in skill.get("skills"):
            if len(Skill.objects.filter(name=newSubSkill.get("name"))) <= 0:
                sub = Skill.objects.create(skillParent = currentSkill,ref=newSubSkill.get("href"),level=newSubSkill.get("lvl"),name=newSubSkill.get("name"),item=newSubSkill.get("item"),itemRef=newSubSkill.get("itemRef"))
                sub.save()

def syncItems(_):
    listItems = ["Recovery","Status","Strengthening","Teleport","Skills","Chests","Collectibles","Ores","IslandItems","Points","Pets","Other"]
    for section in listItems:
        try:
            th = Thread(target=GetAndUpdateItem,args=(section,))
            th.start()
        except Exception as e:
            return JsonResponse(e, safe=False)
    return JsonResponse({"msg": "Sync Items started"}, safe=False)

def syncEquipments(_):
    listItems = ["Swords","Bows","Canes","Claws","Throwing","Armor","Additional","Special","Crystas","AlCrystas","RelicCrystas",]
    pool = ThreadPoolExecutor(max_workers=2)

    for section in listItems:
        try:
            # th = Thread(target=GetAndUpdateItem,args=(section,))
            # th.start()
            pool.submit(GetAndUpdateItem,section)
        except Exception as e:
            return JsonResponse(e, safe=False)
    pool.shutdown(True)
    return JsonResponse({"msg": "Sync Equipments started"}, safe=False)

def GetAndUpdateItem(section):
    items = api.GetRecoveryItems(section)
    ## Check if exists
    newItems =[]
    for item in items:
        with transaction.atomic():
            i = Item.objects.filter(name=item.get("name")).exists()
            if i:
                continue
            newItems.append(Item(name=item.get("name"),desc=item.get("description"),uri=item.get("uri"),type=section))
    if len(newItems) > 0:
        Item.objects.bulk_create(newItems)
