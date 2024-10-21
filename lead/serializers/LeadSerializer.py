from rest_framework import serializers
from ..models import Lead,Employee
from accounts.models import Focus_Segment,Market_Segment,Country,State,Tag
from django.contrib.auth.models import User

class FocusSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Focus_Segment
        fields = ['id','focus_segment']
    
class MarketSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market_Segment
        fields = ['id','market_segment']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','country_name']
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id','state_name']
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','tag']

class EmpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username']





class LeadSerializer(serializers.ModelSerializer):
    market_segment = MarketSegmentSerializer(read_only=True)
    focus_segment = FocusSegmentSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    tags = TagSerializer(many=True)
    lead_owner = serializers.SerializerMethodField() 
    created_by = serializers.SerializerMethodField()  

    class Meta:
        model = Lead
        fields = '__all__'

    def get_lead_owner(self, obj):
        return {
            'id': obj.lead_owner.id,
            'username': obj.lead_owner.username  # Access username directly
        }
    def get_created_by(self, obj):
        return {
            'id': obj.created_by.id,
            'username': obj.created_by.username  # Access username directly
        }

class PostLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Lead
        fields='__all__'