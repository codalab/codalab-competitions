from rest_framework import serializers
from apps.web import models as webmodels
from apps.authenz import models as authmodels


class PageSerial(serializers.ModelSerializer):
    container = serializers.RelatedField(required=False)

    class Meta:
        model = webmodels.Page

    def validate_container(self,attr,source):
        if 'container' in self.context:
            attr['container'] = self.context['container']
        return attr

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


class _CompetitionPhaseSerial(serializers.Serializer):
    phase_id = serializers.IntegerField(required=False)
    competition_id = serializers.IntegerField()
    label = serializers.CharField()
    start_date = serializers.DateField(format='%Y-%m-%d')
    max_submissions = serializers.IntegerField()
    phasenumber = serializers.IntegerField()


class CompetitionPhasesEditSerial(serializers.Serializer):
    competition_id = serializers.IntegerField(required=False)
    phases = _CompetitionPhaseSerial(many=True)
    end_date = serializers.DateField(format='%Y-%m-%d',required=False)
    
    
class CompetitionSerial(serializers.ModelSerializer):
    pages = PageSerial(source='pagecontent__pages',read_only=True)

    class Meta:
        model = webmodels.Competition

class CompetitionParticipantSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionParticipant

class CompetitionSubmissionSerial(serializers.ModelSerializer):
    
    class Meta:
        model = webmodels.CompetitionSubmission
        read_only_fields = ('status','status_details')

class PhaseSerial(serializers.ModelSerializer):
    start_date = serializers.DateField(format='%Y-%m-%d')
    
    class Meta:
        model = webmodels.CompetitionPhase
        
    
    def from_native(self,data):
        print type(data)
        print data
        
class CompetitionPhaseSerial(serializers.ModelSerializer):
    end_date = serializers.DateField(format='%Y-%m-%d')
    phases = PhaseSerial(many=True)

    class Meta:
        model = webmodels.Competition
        fields = ['end_date','phases']

class CompetitionDataSerial(serializers.ModelSerializer):
    image_url = serializers.URLField(source='image.url',read_only=True)
    # phases = CompetitionPhaseSerial(many=True)
    phases = serializers.RelatedField(many=True)

    class Meta:
        model = webmodels.Competition
 


class PhaseRel(serializers.RelatedField):

    def to_native(self,value):
        o = PhaseSerial(instance=value)
        return o.data
        
    def from_native(self,data):
        kw = {'data': data,'partial':self.partial}
        if self.partial:
            instance = webmodels.CompetitionPhase.objects.get(pk=data['id'])
            kw['instance'] = instance
        o = PhaseSerial(**kw)
        print o.data
        print data

        return o

class CSerial(serializers.ModelSerializer):
    phases = PhaseRel(many=True,read_only=False)
    #phases = PhaseSerial(read_only=False,many=True)
    class Meta:
        model = webmodels.Competition
