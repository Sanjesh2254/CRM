from django.http import JsonResponse
from ..models import Log, Task

def delete_log_and_task(request, log_id):
    if request.method == 'DELETE':
        try:
            # Get the log by ID
            log = Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        # Soft delete the log
        log.is_active = False
        log.save()

        # Soft delete the associated Task
        try:
            task = Task.objects.get(contact=log.contact, created_by=log.created_by)
            task.is_active = False
            task.save()
        except Task.DoesNotExist:
            return JsonResponse({'message': 'Task not found'}, status=404)

        return JsonResponse({'message': 'Log and Task deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
