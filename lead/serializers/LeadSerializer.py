from rest_framework import serializers
from ..models import Lead
from accounts.models import Focus_Segment,Market_Segment,Country,State

class leadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class focusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = ['id']
    
class marketSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market_Segment
        fields = ['id']

class countrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id']
    
class stateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id']