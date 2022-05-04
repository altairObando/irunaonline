from ast import arg
from asyncio import subprocess
from django.http import JsonResponse
from .scrapper import Scrapper
from rest.models import Job, JobSkill, Skill
from threading import Thread

import time
# Create your views here.
api = Scrapper()

def index(_):
    return JsonResponse(api.GetPets(), safe=False)

def recoveryItems(_):
    return JsonResponse(api.GetRecoveryItems(), safe=False)

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

def sync(request):
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
