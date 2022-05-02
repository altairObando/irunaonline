from django.shortcuts import render
from django.http import JsonResponse
from .scrapper import Scrapper
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

def skills(_,job):
    return JsonResponse(api.GetSkills(job), safe=False)