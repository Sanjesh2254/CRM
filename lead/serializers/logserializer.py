from rest_framework import serializers
from ..models import Log

class LogSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    focus_segment = serializers.SerializerMethodField()
    log_stage = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    logtype = serializers.SerializerMethodField() 

    class Meta:
        model = Log
        fields = '__all__'

    def get_contact(self, obj):
        return obj.contact.name if obj.contact else None
    
    def get_focus_segment(self, obj):
        return obj.focus_segment.focus_segment if obj.focus_segment else None
    
    def get_log_stage(self, obj):
        return obj.log_stage.stage if obj.log_stage else None
    
    def get_created_by(self, obj):
        return obj.contact.name if obj.contact else None
    
    def get_logtype(self, obj):
        return obj.get_logtype_display()






    #contact, focus_segment, log_stage, created_by