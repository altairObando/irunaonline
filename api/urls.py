from django.urls import path
from .views import index, recoveryItems, item, search, skills, syncDB, syncItems,syncEquipments
urlpatterns = [
    ## Pets information
    path('pets/', index, name="petskills" ),
    ## list of items
    path('items/<section>', recoveryItems, name="all items" ),
    ## Get item info and more.
    path('item/<itemname>', item),
    ## Searchs on site.
    path('search/<search>', search),
    ## Skills of a job
    path('skills/<job>', skills),
    ## Sync all Skills to DB
    path('sync/',syncDB),
    path('syncItems/', syncItems),
    path('syncEquipments/',syncEquipments)
]