from rest_framework import serializers
from ..models import Contact, Lead, Contact_Status, Lead_Source
from django.contrib.auth.models import User

from rest_framework import serializers
from ..models import Contact

class ContactSerializer(serializers.ModelSerializer):
    lead = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    lead_source = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = '__all__'


def get_lead(self, obj):
    if obj.lead:
        return {"id": obj.lead.id, "lead": obj.lead.name}
    return None

def get_status(self, obj):
    if obj.status:
        return {"id": obj.status.id, "contact_status": obj.status.status}
    return None


def get_lead_source(self, obj):
    if obj.lead_source:
        return {"id": obj.lead_source.id, "lead_source": obj.lead_source.source}
    return None

def get_created_by(self, obj):
    if obj.created_by:
        return {"id": obj.created_by.id, "created_by": obj.created_by.get_full_name()}
    return None
class ContactStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Status
        fields = ['id','status']



class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead_Source
        fields = ['id','source']