from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest.models import Skill
from rest.serializers import SkillSerializer


class SkillViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer

    @action(methods=["GET"], detail=False)
    def search(self, request):
        params = request.query_params
        jobName   = params.get("job")
        skillName = params.get("name")
        level     = params.get("level")

        queryResult = self.queryset
        if jobName and jobName is not None:
            queryResult = queryResult.filter(skillParent__Job__name__contains=jobName)
        if skillName and skillName is not None:
            queryResult = queryResult.filter(name__contains=skillName)
        if level and level is not None:
            queryResult = queryResult.filter(level__contains=level)
        
        if len(queryResult) > 0:
            serial = SkillSerializer(queryResult, many=True)
            return Response({ "total": len(queryResult), "data": serial.data, "ok": True })
        return Response({ "total": 0, "data": [], "ok": False })
