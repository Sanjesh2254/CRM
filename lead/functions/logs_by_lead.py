from ..models import Contact, Log
from ..serializers.logserializer import LogSerializer
from django.http import JsonResponse

def get_logs_by_lead(request, lead_id):
    try:
        contacts = Contact.objects.filter(lead_id=lead_id)
        logs = Log.objects.filter(conatct__in=contacts)

        log_serialier = LogSerializer(logs, many=True)
        return JsonResponse(log_serialier.data, safe = False, statsus =200)
    except Contact.DoesNotExist:
        return JsonResponse({'message': 'No contacts found for this lead'}, status = 404)