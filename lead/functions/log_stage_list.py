from django.http import JsonResponse
from ..models import Log_Stage
from ..serializers.logstageserializer import LogStageSerializer

def get_log_stages(request):
    if request.method == 'GET':
        log_stages = Log_Stage.objects.filter(is_active=True)  
        serializer = LogStageSerializer(log_stages, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
