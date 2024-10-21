from rest_framework import serializers
from ..models import Log

class LogSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = '__all__'

    def get_contact(self, obj):
        return obj.contact.name if obj.contact else None
    






    #contact, focus_segment, log_stage, created_by