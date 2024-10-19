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
        return obj.lead.name if obj.lead else None

    def get_status(self, obj):
        return obj.status.status if obj.status else None

    def get_lead_source(self, obj):
        return obj.lead_source.source if obj.lead_source else None

    def get_created_by(self, obj):
        return obj.created_by.first_name if obj.created_by else None