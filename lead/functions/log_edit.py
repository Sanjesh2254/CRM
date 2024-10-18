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

            # Now update the corresponding Task
            try:
                task = Task.objects.get(contact=log.contact, created_by=log.created_by)
            except Task.DoesNotExist:
                return JsonResponse({'message': 'Task not found'}, status=404)

            # Update task details based on the updated log
            task_data = {
                'task_date_time': log.follow_up_date_time,
                'task_detail': log.details
            }
            task_serializer = TaskSerializer(task, data=task_data, partial=True)
            if task_serializer.is_valid():
                task_serializer.save()
                return JsonResponse({'message': 'Log and Task updated successfully'}, status=200)
            return JsonResponse(task_serializer.errors, status=400)
        return JsonResponse(log_serializer.errors, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
