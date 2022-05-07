from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest.models import Item
from rest.serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Item.objects.all().order_by("type")
    serializer_class = ItemSerializer

    @action(methods=["GET"], detail=False)
    def search(self, request):
        params = request.query_params
        name   = params.get("name")
        desc   = params.get("desc")
        itemType   = params.get("type")
        queryResult = self.queryset
        if itemType and itemType is not None:
            queryResult = queryResult.filter(type=itemType)
        if name and name is not None:
            queryResult = queryResult.filter(name__contains=name)
        if desc and desc is not None:
            queryResult = queryResult.filter(desc__contains=desc)
        
        ## No query
        if (name == itemType and desc == itemType and itemType is None):
            queryResult = []

        if len(queryResult) > 0:
            serial = ItemSerializer(queryResult, many=True)
            return Response({ "total": len(queryResult), "data": serial.data, "ok": True })
        return Response({ "total": 0, "data": [], "ok": False })
