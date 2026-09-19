from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Table
from .serializers import TableSerializer


class TableViewSet(viewsets.ModelViewSet):
    """
    CRUD for tables, plus GET /api/tables/available/?party_size=4
    -> tables currently free with enough capacity.
    """
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'location']
    ordering_fields = ['number', 'capacity']

    @action(detail=False, methods=['get'])
    def available(self, request):
        qs = self.get_queryset().filter(status='available')
        party_size = request.query_params.get('party_size')
        if party_size:
            qs = qs.filter(capacity__gte=int(party_size))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
