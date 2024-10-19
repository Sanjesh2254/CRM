from django.http import JsonResponse
from ..models import Log, Contact, Log_Stage, Task
from ..serializers.logserializer import LogSerializer
from ..serializers.taskserializer import TaskSerializer
from django.contrib.auth.models import User
import json

def create_log(request, contact_id):
    if request.method == 'POST':
        try:
            contact = Contact.objects.get(id=contact_id)
            lead = contact.lead  # Get the related lead to retrieve focus_segment
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'Contact not found'}, status=404)

        try:
            data = json.loads(request.body)  # If JSON request, use request.body
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

        log_stage_id = data.get('log_stage')  # Now using the JSON body
        try:
            log_stage = Log_Stage.objects.get(id=log_stage_id)
        except Log_Stage.DoesNotExist:
            return JsonResponse({'message': 'Log stage not found'}, status=404)
        
        # Hardcode a specific user for 'created_by' for testing purposes
        created_by_user = User.objects.get(id=2)

        # Prepare log data
        log_data = {
            'contact': contact.id,
            'focus_segment': lead.focus_segment.id,
            'follow_up_date_time': data.get('follow_up_date_time'),
            'log_stage': log_stage.id,
            'details': data.get('details'),
            'file': request.FILES.get('file'),
            'created_by': created_by_user.id,
            
        }

        # Serialize the data and create the log
        log_serializer = LogSerializer(data=log_data)
        if log_serializer.is_valid():
            log = log_serializer.save()  # Save the Log
            
            # Check if follow_up_date_time exists before creating a Task
            if log.follow_up_date_time:
                task_data = {
                    'contact': contact.id,
                    'log': log.id,
                    'task_date_time': log.follow_up_date_time,
                    'task_detail': log.details,
                    'created_by': created_by_user.id,  # request.user.id,   Pass the user ID
                    'is_active': True,
                    'tasktype' : 'A',
                }
                task_serializer = TaskSerializer(data=task_data)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task created successfully'}, status=201)
                else:
                    log.delete()
                    return JsonResponse(task_serializer.errors, status=400)
            else:
                return JsonResponse({'message': 'Log created successfully'}, status=201)
        
        return JsonResponse(log_serializer.errors, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)