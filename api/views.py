from django.http import JsonResponse
from .scrapper import Scrapper
from rest.models import Job, JobSkill, Skill
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


def updateSkills(job, requestSkill):
    #Recuperar el job
    dbJob = Job.objects.get(name=job)
    if dbJob is None:
        return JsonResponse({'error': True, 'msg': ('%s not found in db' % job)})
    for skill in requestSkill:
        currentSkill = JobSkill.objects.filter(name=skill.get("name")).first()
        if currentSkill is None:
            currentSkill = JobSkill.objects.create(name=skill.get("name"),description=skill.get("description"),Job=dbJob )
            currentSkill.save()
        for newSubSkill in skill.get("skills"):
            if len(Skill.objects.filter(name=newSubSkill.get("name"))) <= 0:
                sub = Skill.objects.create(skillParent = currentSkill,ref=newSubSkill.get("href"),level=newSubSkill.get("lvl"),name=newSubSkill.get("name"),item=newSubSkill.get("item"),itemRef=newSubSkill.get("itemRef"))
                sub.save()
