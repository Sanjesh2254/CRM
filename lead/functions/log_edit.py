from django.http import JsonResponse
from ..models import Log, Task
from ..serializers.logserializer import LogSerializer
from ..serializers.taskserializer import TaskSerializer
import json

def edit_log_and_task(request, log_id):
    if request.method == 'PUT':
        try:
            # Get the log by ID
            log = Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        # Parse request data
        data = json.loads(request.body)

        # Update log fields
        log_serializer = LogSerializer(log, data=data, partial=True)
        if log_serializer.is_valid():
            log = log_serializer.save()  # Save the updated log

            # Check if the follow_up_date_time is in the PUT request
            follow_up_date_time = data.get('follow_up_date_time')
            
            if follow_up_date_time:
                try:
                    # Try to get a task associated with this log
                    task = Task.objects.get(log=log)
                except Task.DoesNotExist:
                    # If no task exists, create a new one
                    task_data = {
                        'contact': log.contact.id,
                        'log': log.id,
                        'task_date_time': follow_up_date_time,  # Use new follow_up_date_time
                        'task_detail': log.details,  # Use log details (updated or existing)
                        'created_by': log.created_by.id,  # Use the same user who created the log
                        'is_active': True,
                        'tasktype': 'A',  # Assuming it's an automatic task
                    }
                    task_serializer = TaskSerializer(data=task_data)
                    if task_serializer.is_valid():
                        task_serializer.save()
                        return JsonResponse({'message': 'Log updated and new Task created successfully'}, status=200)
                    else:
                        return JsonResponse(task_serializer.errors, status=400)
                
                # If task already exists, update it
                task_data = {
                    'task_date_time': follow_up_date_time,
                    'task_detail': log.details  # Update task with new log details
                }
                task_serializer = TaskSerializer(task, data=task_data, partial=True)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task updated successfully'}, status=200)
                return JsonResponse(task_serializer.errors, status=400)
            else:
                return JsonResponse({'message': 'Log updated successfully, no task changes'}, status=200)

        return JsonResponse(log_serializer.errors, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
