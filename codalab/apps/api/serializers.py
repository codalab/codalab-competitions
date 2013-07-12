from rest_framework import serializers
from apps.web import models as webmodels
from apps.authenz import models as authmodels


class CompetitionDatasetSerial(serializers.ModelSerializer):
    dataset_id = serializers.IntegerField()
    source_url = serializers.URLField()
    source_address_info = serializers.CharField()
    competition_id = serializers.IntegerField()
    phase_id = serializers.IntegerField()
    
    def validata_phase_id(self,attr,source):
        if not attr[source]:
            attr[source] = None
        return attr

    def save():
        pass

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
 
class ContentContainerSerialBase(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source='type.pk')
    type_name = serializers.CharField(source='type.name')
    type_codename = serializers.CharField(source='type.codename')
    visibility_id = serializers.IntegerField(source='visibility.pk')
    visibility_name = serializers.CharField(source='visibility.name')
    visibility_codename = serializers.CharField(source='visibility.codename')
    
    class Meta:
        model = webmodels.ContentContainer
        #exclude = ('parent','type','visibility')
        #fields = ('id', 'type_id','type_name','visibility_id','visibility_name' ,'rank','max_items','children')

class ContentContainerSerial(ContentContainerSerialBase):
    children = ContentContainerSerialBase(source='children')
    


class PageSerial(serializers.ModelSerializer):
    
    def __init__(self ,*args, **kwargs):
        super(PageSerial,self).__init__(*args,**kwargs)
        self._pagecontainer = self.context.get('pagecontainer',None)
       

    def validate_pagecontainer(self, attrs, source):
        if self._pagecontainer:
            attrs['pagecontainer'] = self._pagecontainer
        return attrs

    class Meta:
        model = webmodels.Page

class PageContainerSerial(serializers.ModelSerializer):
    pages = PageSerial(source='pages')
    
    class Meta:
        model = webmodels.PageContainer
        
