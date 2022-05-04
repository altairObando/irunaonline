from django.urls import path
from .views import index, recoveryItems, item, search, skills
urlpatterns = [
    ## Pets information
    path('pets/', index, name="petskills" ),
    ## list of recovery items
    path('items/recovery', recoveryItems, name="recoveryItems" ),
    ## Get item info and more.
    path('item/<itemname>', item),
    ## Searchs on site.
    path('search/<search>', search),
    ## Skills of a job
    path('skills/<job>', skills)
]