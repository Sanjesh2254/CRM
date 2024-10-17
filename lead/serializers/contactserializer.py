from rest_framework import serializers
from ..models import Contact  # Import the Contact model

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'