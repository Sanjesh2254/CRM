from django.http import JsonResponse
from ..models import Log
from ..serializers.logserializer import LogSerializer
def get_logs_by_contact(request, contact_id):
    try:
        logs = Log.objects.filter(contact_id=contact_id)
        log_serializer =  LogSerializer(logs, many=True)
        return JsonResponse(log_serializer.data, safe=False, status=200)
    except Log.DoesNotExist:
        return JsonResponse({'message': 'Log does no exist'}, status =404)