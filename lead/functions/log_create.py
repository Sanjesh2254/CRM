from django.http import JsonResponse
from ..models import Log, Contact, Log_Stage, Task
from ..serializers.logserializer import LogSerializer
from ..serializers.taskserializer import TaskSerializer
from django.contrib.auth.models import User

def create_log(request, contact_id):
    if request.method == 'POST':
        try:
            # Get the contact by ID
            contact = Contact.objects.get(id=contact_id)
            lead = contact.lead  # Get the related lead to retrieve focus_segment
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'Contact not found'}, status=404)

        # Get Log Stage
        try:
            log_stage = Log_Stage.objects.get(id=request.POST.get('log_stage'))
        except Log_Stage.DoesNotExist:
            return JsonResponse({'message': 'Log stage not found'}, status=404)

        # Hardcode a specific user for 'created_by' for testing purposes
        created_by_user = User.objects.get(id=2)  
        

        # Prepare log data
        log_data = {
            'contact': contact.id,
            'focus_segment': lead.focus_segment.id,
            'follow_up_date_time': request.POST.get('follow_up_date_time'),
            'log_stage': log_stage.id,
            'details': request.POST.get('details'),
            'file': request.FILES.get('file'),
            'created_by': created_by_user.id,   #request.user.id,  # Pass the user ID 
        }

        # Serialize the data and create the log
        log_serializer = LogSerializer(data=log_data)
        if log_serializer.is_valid():
            log = log_serializer.save()  # Save the Log

            # Now create a Task based on the log details
            task_data = {
                'contact': contact.id,
                'task_date_time': log.follow_up_date_time,  # Use the log's follow-up date
                'task_detail': log.details,  # Use the log's details
                'created_by': created_by_user.id,  # Same user as log
                'is_active': True
            }

            # Serialize the task data and create the task
            task_serializer = TaskSerializer(data=task_data)
            if task_serializer.is_valid():
                task_serializer.save()
                return JsonResponse({'message': 'Log and Task created successfully'}, status=201)
            else:
                # If Task creation fails, delete the created Log
                log.delete()
                return JsonResponse(task_serializer.errors, status=400)
        return JsonResponse(log_serializer.errors, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)
