from django.shortcuts import render
from django.http import JsonResponse
from .scrapper import Scrapper
# Create your views here.
api = Scrapper()

def index(req):
    return JsonResponse(api.GetPets(), safe=False)

def recoveryItems(req):
    return JsonResponse(api.GetRecoveryItems(), safe=False)

def item(req, itemname):
    return JsonResponse(api.GetFullItem(itemname), safe=False)