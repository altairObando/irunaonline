from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest.models import Job
from rest.serializers import JobSerializer
# Create your views here.
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("name")
    serializer_class = JobSerializer

    @action(methods=["GET"],detail=False)
    def search(self, request):
        jobName = request.query_params.get("name")
        result = self.queryset.filter(name__contains=jobName)
        if len(result) > 0:
            serializer = JobSerializer(result, many=True)
            return Response({ "total": len(result), "data": serializer.data })

        return Response({ "total": 0, "data": [], "Ok": False })
