from ast import arg
from asyncio import subprocess
from concurrent.futures import ThreadPoolExecutor
import json
from django.http import JsonResponse
from .scrapper import Scrapper
from rest.models import Job, JobSkill, Skill, Item, Monster, MonsterDrops
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
    pool = ThreadPoolExecutor(max_workers=1)
    for section in listItems:
        try:
            pool.submit(GetAndUpdateItem,section)
        except Exception as e:
            return JsonResponse(e, safe=False)
    pool.shutdown(True)
    return JsonResponse({"msg": "Sync Items started"}, safe=False)

def syncEquipments(_):
    listItems = ["Swords","Bows","Canes","Claws","Throwing","Armor","Additional","Special","Crystas","AlCrystas","RelicCrystas"]
    pool = ThreadPoolExecutor(max_workers=1)

    for section in listItems:
        try:
            pool.submit(GetAndUpdateItem,section)
        except Exception as e:
            return JsonResponse(e, safe=False)
    pool.shutdown(True)
    return JsonResponse({"msg": "Sync Equipments started"}, safe=False)

pool = ThreadPoolExecutor(max_workers=2)
def syncDB(_):    
    try:
        items = list(Item.objects.all())
        currentGroup = 0
        for slice in range(40, len(items), 40):
            g = items[currentGroup: slice]
            isLast = (currentGroup + 40 ) == len(items)
            print("Encolando %d - %d de %d" % (currentGroup, slice, len(items)))
            pool.submit(syncEquipmentsDB, g, isLast )
            currentGroup = currentGroup + 40
            
    except Exception as e:
        print(e)
    return JsonResponse({"msg": "Sync Equipments started"}, safe=False)

def syncEquipmentsDB(items,last=False):    
    checkDrops = []
    for item in items:
        web_name = item.uri.split('/')[2]
        time.sleep(1)
        desc = api.GetFullItem(web_name)
        print("Updating: %s" % web_name)
        drop = "%s-%s" % (item.uri,desc.get("name"))
        if drop not in checkDrops:
            checkDrops.append({ "name": item.uri, "info": desc.get("more") })
    SyncDrop(checkDrops, last)  

def SyncDrop(drops,last=False):
    bulkMonsters = []
    waiting = []
    for drop in drops:
        ## Search item
        item = Item.objects.get(uri=drop.get("name"))
        if item is None:
            continue ## cant add drop
        ## Check Monster drop
        if drop.get("info").get("Monsters") is None:
            continue
        for monster in drop.get("info").get("Monsters"):
            ## check if monster exists
            newMonster = Monster.objects.filter(name=monster.get("name")).first()
            if newMonster is None:
                with transaction.atomic():
                    attr = json.dumps(monster.get("attr"))
                    Weak = json.dumps(monster.get("weak"))
                    newMonster = Monster.objects.create(name=monster.get("name"),imgSrc=monster.get("imgSrc"),attr=attr,weak=Weak)
                    newMonster.save()
            ## check if drop is added
            exist = MonsterDrops.objects.filter(baseItem=item).filter(baseMonster=newMonster).exists()
            wait = "%s-%s" % (item.name,newMonster.name)
            if exist and wait not in waiting:
                continue
            bulkMonsters.append(MonsterDrops(baseMonster=newMonster,baseItem=item))
            waiting.append(wait)
    if len(bulkMonsters) > 0:
        print("%d monster drops added" % len(bulkMonsters))
        MonsterDrops.objects.bulk_create(bulkMonsters)
    if last:
        pool.shutdown(True)


def GetAndUpdateItem(section):
    items = api.GetRecoveryItems(section)
    currentItems = Item.objects.all()
    ## Check if exists
    newItems =[]
    checkDrops =[]
    for item in items:
        with transaction.atomic():
            i = currentItems.filter(name=item.get("name")).exists()
            ## Check full data
            name = item.get("uri").split('/')[2]
            full = api.GetFullItem(name)
            checkDrops.append({ "name": item.get("uri"), "info": full.get("more") })
            if i :
                ## Update component
                i.atk = item.get("atk")
                i.deff= item.get("def")
                i.notes=item.get("notes")
                if item.get("img"):
                    i.imageAlt = item.get("img").get("name")
                    i.imgSrc   = item.get("img").get("src")
                i.save()
                continue
            newItems.append(Item(name=item.get("name"),desc=item.get("description"),uri=item.get("uri"),type=section))
    if len(newItems) > 0:
        Item.objects.bulk_create(newItems)
    SyncDrop(checkDrops)
