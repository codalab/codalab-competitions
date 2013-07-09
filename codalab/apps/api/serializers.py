from rest_framework import serializers
from apps.web import models as webmodels
from apps.authenz import models as authmodels

       

class CompetitionSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.Competition

class CompetitionParticipantSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionParticipant

class CompetitionPhaseSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionPhase

class CompetitionDataSerial(serializers.ModelSerializer):

    class Meta:
        model = webmodels.Competition
 

class ContentContainerSerial(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source='type.pk')
    type_name = serializers.CharField(source='type.name')

    class Meta:
        model = webmodels.ContentContainer
        depth = 1
        exclude = ('parent','type')
        fields = ('type_id','type_name','visibility','label','rank','max_items','children')

class PageSerial(serializers.ModelSerializer):

    class Meta:
        model = webmodels.Page

class PageContainerSerial(serializers.ModelSerializer):
    pages = PageSerial(source='pages')

    class Meta:
        model = webmodels.PageContainer
        
