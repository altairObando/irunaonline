from tkinter import N
from django.urls import path
from .views import index, recoveryItems, item
urlpatterns = [
    path('pets/', index, name="petskills" ),
    path('items/recovery', recoveryItems, name="recoveryItems" ),
    path('items/search/<itemname>', item),
]