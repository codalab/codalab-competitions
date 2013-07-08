from rest_framework import serializers
from apps.web import models as webmodels
from apps.authenz import models as authmodels

class CompetitionDataSerial(serializers.ModelSerializer):

    class Meta:
        model = webmodels.Competition
        

    

class CompetitionParticipantSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionParticipant

class CompetitionPhaseSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionPhase
