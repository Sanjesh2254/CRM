from rest_framework import serializers
from ..models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class GetTaskSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    log = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    tasktype = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = '__all__'


    def get_contact(slef, obj):
        return {
            'id' : obj.contact.id,
            'name': obj.contact.name
        } if obj.contact else None
    
    def get_log(slef, obj):
        return {
            'id' : obj.log.id,
            'log' : obj.log.details
        } if obj.log else None
    
    def get_created_by(slef, obj):
        return {
            'id': obj.created_by.id,
            'username' : obj.created_by.username
        } if obj.created_by else None
    
    def get_tasktype(slef, obj):
        return {
            'code' : obj.tasktype,
            'label' : obj.get_tasktype_display()
        }