from . import serializers
from rest_framework import (viewsets,views)
from apps.web import models as webmodels
from apps.authenz import models as authmodels

class CompetitionAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionDataSerial
    queryset = webmodels.Competition.objects.all()


class CompetitionParticipantAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionParticipantSerial
    queryset = webmodels.CompetitionParticipant.objects.all()


class CompetitionPhaseAPIViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CompetitionPhaseSerial
    queryset = webmodels.CompetitionPhase.objects.all()
    
    def get_query_set(self):
        # The pk (primary key) is for the competition, not the phase.
        # rest framework could use a little extension to provide more 
        # flexibility.
        competition_id = self.kwargs.get('pk',None)
        phasenumber = self.kwargs.get('phasenumber',None)
        kw = {}
        if competition_id:
            kw['competition_id'] = competition_id
        if number:
            kw['phasenumber'] = phasenumber
        return self.queryset.filter(**kw)

competitionphase_list = CompetitionPhaseAPIViewset.as_view({'get':'list'})
competitionphase_retrieve = CompetitionPhaseAPIViewset.as_view({'get':'retrieve'})


class ContentContainerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ContentContainerSerial
    queryset = webmodels.ContentContainer.objects.filter(parent=None)
