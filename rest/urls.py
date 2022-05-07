from django.urls import path, include
from rest_framework import routers
from rest.Views import JobsView, ItemView, SkillsView

router = routers.DefaultRouter()
router.register(r'items', ItemView.ItemViewSet )
router.register(r'jobs', JobsView.JobViewSet)
router.register(r'skills', SkillsView.SkillViewSet)

urlpatterns = [
    path("", include(router.urls))
]