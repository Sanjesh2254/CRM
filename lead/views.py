from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response

from lead.models import Contact
from lead.serializers.contactserializer import ContactSerializer

    

class Contact_Create(APIView):


    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    

class Contact_Delete(APIView):

    def put(self, request,contact_id):
        try:
            contact = Contact.objects.get(contact_id=contact_id)
            contact.is_active=False
            contact.save()
            return Response({"message": "Contact deactivate"}, status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # def delete(self,request, pk):
    #  try:
    #     contact = Contact.objects.get(pk=pk)
    #     contact.delete()
    #     return Response({"message":"contact deactivate"},status=status.HTTP_204_NO_CONTENT)
    #  except Contact.DoesNotExist:
    #     return Response({"error":"contact not found"},status=status.HTTP_404_NOT_FOUND)
     

class Contact_Update(APIView): 
  
 def post(self,request,contact_id):
    try:
        contact = Contact.objects.get(contact_id=contact_id)
        serializer = ContactSerializer(contact, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Contact.DoesNotExist:
        return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
    









# ***********Afsal******
from django.http import JsonResponse
import json
from .models import Log_Stage, Log, Task, Lead_Assignment
from django.contrib.auth.models import User
from .serializers.logserializer import LogSerializer
from .serializers.taskserializer import TaskSerializer
from .serializers.employeeserializer import EmployeeSerializer
from .serializers.logstageserializer import LogStageSerializer


# Employee List View
class EmployeeListView(APIView):
    def get(self, request):
        employees = User.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

# Lead Assignment View
class LeadAssignmentView(APIView):
    def post(self, request, lead_id):
        assigned_by_user = User.objects.get(id=3)
        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return JsonResponse({"message": "Lead not found"}, status=404)
        
        data = json.loads(request.body)
        assigned_to_ids = data.get('assigned_to')  # Expecting list of user IDs

        if not assigned_to_ids:
            return JsonResponse({"message": "No employees selected"}, status=400)

        # Iterate through selected users and create Lead_Assignment records
        for user_id in assigned_to_ids:
            try:
                user = User.objects.get(id=user_id)  # Get a single user instance
                Lead_Assignment.objects.create(lead=lead, assigned_to=user, assigned_by=assigned_by_user)  # Create a record for each user
            except User.DoesNotExist:
                return JsonResponse({"message": f"User {user_id} not found"}, status=404)

        return JsonResponse({"message": "Lead assigned successfully"}, status=201)
    
# Call the function to get contact detail
class ContactDetailView(APIView):
    def get(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)  # Fetch the contact by ID
            serializer = ContactSerializer(contact)
            return JsonResponse(serializer.data, status=200)
        except Contact.DoesNotExist:
            return JsonResponse({"message": "Contact not found"}, status=404)

# Creating, Editing, Deleting Log and Task
class LogManagement(APIView):
    
    # Create Log and Task
    def post(self, request, id):
        try:
            contact = Contact.objects.get(id=id)
            lead = contact.lead  # Get the related lead to retrieve focus_segment
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'Contact not found'}, status=404)

        
        data = request.data
        
        log_stage_id = data.get('log_stage')
        try:
            log_stage = Log_Stage.objects.get(id=log_stage_id)
        except Log_Stage.DoesNotExist:
            return JsonResponse({'message': 'Log stage not found'}, status=404)

        # Hardcoded user for testing purposes
        created_by_user = User.objects.get(id=2)

        log_data = {
            'contact': contact.id,
            'focus_segment': lead.focus_segment.id,
            'follow_up_date_time': data.get('follow_up_date_time'),
            'log_stage': log_stage.id,
            'details': data.get('details'),
            'file': request.FILES.get('file'),
            'created_by': created_by_user.id,
        }

        log_serializer = LogSerializer(data=log_data)
        if log_serializer.is_valid():
            log = log_serializer.save()  # Save the log

            if log.follow_up_date_time:
                task_data = {
                    'contact': contact.id,
                    'log': log.id,
                    'task_date_time': log.follow_up_date_time,
                    'task_detail': log.details,
                    'created_by': created_by_user.id,
                    'is_active': True,
                    'tasktype': 'A',
                }
                task_serializer = TaskSerializer(data=task_data)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task created successfully'}, status=201)
                else:
                    log.delete()  # Rollback log creation if task fails
                    return JsonResponse(task_serializer.errors, status=400)
            else:
                return JsonResponse({'message': 'Log created successfully'}, status=201)

        return JsonResponse(log_serializer.errors, status=400)

    # Edit Log and Task
    def put(self, request, id):
        try:
            log = Log.objects.get(id=id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        data = request.data
        log_serializer = LogSerializer(log, data=data, partial=True)

        if log_serializer.is_valid():
            log = log_serializer.save()

            follow_up_date_time = data.get('follow_up_date_time')
            if follow_up_date_time:
                try:
                    task = Task.objects.get(log=log)
                except Task.DoesNotExist:
                    task_data = {
                        'contact': log.contact.id,
                        'log': log.id,
                        'task_date_time': follow_up_date_time,
                        'task_detail': log.details,
                        'created_by': log.created_by.id,
                        'is_active': True,
                        'tasktype': 'A',
                    }
                    task_serializer = TaskSerializer(data=task_data)
                    if task_serializer.is_valid():
                        task_serializer.save()
                        return JsonResponse({'message': 'Log updated and new Task created successfully'}, status=200)
                    else:
                        return JsonResponse(task_serializer.errors, status=400)

                task_data = {
                    'task_date_time': follow_up_date_time,
                    'task_detail': log.details,
                }
                task_serializer = TaskSerializer(task, data=task_data, partial=True)
                if task_serializer.is_valid():
                    task_serializer.save()
                    return JsonResponse({'message': 'Log and Task updated successfully'}, status=200)
                return JsonResponse(task_serializer.errors, status=400)

            # If no follow_up_date_time, only update the task detail if the task exists
            try:
                task = Task.objects.get(log=log)
                task_data = {
                    'task_detail': log.details
                }
                task_serializer = TaskSerializer(task, data=task_data, partial=True)
                if task_serializer.is_valid():
                    task_serializer.save()
                return JsonResponse({'message': 'Log updated successfully,  task changes'}, status=200)
            except Task.DoesNotExist:
                return JsonResponse({'message': 'Log updated, no task changes'}, status=200)

        return JsonResponse(log_serializer.errors, status=400)

    # Delete Log and Task
    def delete(self, request, id):
        try:
            log = Log.objects.get(id=id)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log not found'}, status=404)

        log.is_active = False
        log.save()

        try:
            task = Task.objects.get(log =log )
            task.is_active = False
            task.save()
        except Task.DoesNotExist:
            return JsonResponse({'message': 'Task not found'}, status=404)

        return JsonResponse({'message': 'Log and Task deleted successfully'}, status=200)

# Calling log_status for creating Log
class LogStageListView(APIView):
    def get(self, request):
            log_stages = Log_Stage.objects.filter(is_active=True)  
            serializer = LogStageSerializer(log_stages, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)
        
#Calling all the logs in a Lead
class logsbyLeadsView(APIView):
    def get(self, request, lead_id):
        try:
            contacts = Contact.objects.filter(lead_id=lead_id)
            logs = Log.objects.filter(contact__in=contacts, is_active = True)

            log_serializer = LogSerializer(logs, many=True)
            return JsonResponse(log_serializer.data, safe = False, status=200)
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'No contacts found for this lead'}, status = 404)

#calling all the logs of a Contact
class logsbyContactView(APIView):
    def get(self, request, contact_id):
        try:
            logs = Log.objects.filter(contact_id=contact_id, is_active = True)
            log_serializer =  LogSerializer(logs, many=True)
            return JsonResponse(log_serializer.data, safe=False, status=200)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log does not exist'}, status =404)
    

#--------sankar----------



from lead.models import Lead
from lead.serializers.leadgetserializer import GetallLeadSerializer
from django.shortcuts import get_object_or_404

class leadfilterView(APIView):
    def get(self, request):
        leads = Lead.objects.all()  
        focus_segment_id = request.query_params.getlist('focus_segment')
        vertical_id = request.query_params.get('vertical_id')
        state_id = request.query_params.get('state')
        country_id = request.query_params.get('country')
        created_on = request.query_params.get('created_on')
        annual_revenue = request.query_params.get('annual_revenue')


        if focus_segment_id: 
            leads = leads.filter(focus_segment__id__in=focus_segment_id)

        if vertical_id: 
            leads = leads.filter(focus_segment__vertical__id=vertical_id)

        if state_id: 
            leads = leads.filter(state_id=state_id)

        if country_id:
            leads = leads.filter(country_id=country_id)

        if created_on:
            leads = leads.filter(created_on=created_on)

        if annual_revenue:
            leads = leads.filter(annual_revenue=annual_revenue)

        serializer = GetallLeadSerializer(leads, many=True)
        return Response(serializer.data)
    


#--------------------sabari----

from .functions.lead import create_lead,delete_lead,deactivate_lead,update_lead,market_segment_list,focus_segment_list,country_list,state_list
from rest_framework.decorators import api_view
from rest_framework.views import APIView


class create(APIView):
    def post(self,request):
        return create_lead(request)
    
class update(APIView):
    def put(self,request,lead_id):
        return update_lead(request,lead_id)
    
# class permanent_delete(APIView):
#     def delete(self,request,lead_id):
#         return delete_lead(request,lead_id)

class delete(APIView):
    def put(self,request,lead_id):
        return deactivate_lead(request,lead_id)

class market_segment_list_view(APIView):
    def get(self,request):
        return market_segment_list(request)
    
class focus_segment_list_view(APIView):
    def get(self,request):
        return focus_segment_list(request)
    
class country_list_view(APIView):
    def get(self,request):
        return country_list(request)

class state_list_view(APIView):
    def get(self,request,country_id):
        return state_list(request,country_id)


#--------------sumith--------

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Task, Contact
from .serializers.taskserializer import TaskSerializer

class CreateTaskView(APIView):
    def post(self, request):
        assigned_by_user = User.objects.get(id=2)
        try:
            contact_id = request.data.get('contact_id')  # Get contact ID from request body
            log_id = Log.objects.get(id=request.data.get('log_id'))  # Get contact ID from request body
            task_date_time = request.data.get('task_date_time')  # Get date and time
            task_detail = request.data.get('task_detail')  # Get task details
            task_type = 'M'  # Task type is manual

            # Get the Contact object
            contact = Contact.objects.get(id=contact_id)

            # Create a task instance
            task = Task.objects.create(
                contact=contact,
                log=log_id,
                task_date_time=task_date_time,
                task_detail=task_detail,
                created_by=assigned_by_user,  # You can replace it with request.user for dynamic assignment
                tasktype=task_type
            )

            serializer = TaskSerializer(task)
            return Response({"message":"Task created sucessfully"}, status=status.HTTP_201_CREATED)

        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#-----For PUT & DELETE (Is_active=false)-------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Task, Contact, Log, Task_Assignment
from .serializers.taskserializer import TaskSerializer, GetTaskSerializer
from django.utils.timezone import now, timedelta

class TaskManagement(APIView):
    def get(self, request, id):
        try:
            # Get the user object
            user = User.objects.get(id=id)

            # 1. Gather all tasks that are associated with leads owned by the user
            leads_owned_by_user = Lead.objects.filter(lead_owner=user)
            tasks_related_to_leads = Task.objects.filter(contact__lead__in=leads_owned_by_user)

            # 2. Gather all tasks directly associated with the user (created_by or assigned_to)
            tasks_created_by_user = Task.objects.filter(created_by=user)
            tasks_assigned_to_user = Task_Assignment.objects.filter(assigned_to=user).values_list('task', flat=True)
            tasks_assigned_to_user = Task.objects.filter(id__in=tasks_assigned_to_user)

            # Combine both querysets and remove duplicates
            all_tasks = tasks_related_to_leads | tasks_created_by_user | tasks_assigned_to_user
            all_tasks = all_tasks.distinct()

            # Current time and time ranges
            today = now().date()
            tomorrow = today + timedelta(days=1)
            next_7_days = today + timedelta(days=7)

            # Categorize tasks
            tasks_today = all_tasks.filter(task_date_time__date=today)
            tasks_tomorrow = all_tasks.filter(task_date_time__date=tomorrow)
            tasks_next_7_days = all_tasks.filter(task_date_time__date__range=[tomorrow + timedelta(days=1), next_7_days])

            # Serialize the tasks for each category
            tasks_today_serialized = GetTaskSerializer(tasks_today, many=True).data
            tasks_tomorrow_serialized = GetTaskSerializer(tasks_tomorrow, many=True).data
            tasks_next_7_days_serialized = GetTaskSerializer(tasks_next_7_days, many=True).data

            # Response data
            response_data = {
                'tasks_today': tasks_today_serialized,
                'tasks_tomorrow': tasks_tomorrow_serialized,
                'tasks_next_7_days': tasks_next_7_days_serialized,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        assigned_by_user = User.objects.get(id=2)  # Static assignment, change if needed
        try:
            # Retrieve the task object
            task = Task.objects.get(id=id)

            # Get data from request body
            contact_id = request.data.get('contact_id')
            log_id = Log.objects.get(id=request.data.get('log_id')) if request.data.get('log_id') else None
            task_date_time = request.data.get('task_date_time')
            task_detail = request.data.get('task_detail')
            task_type = request.data.get('tasktype', 'M')  # Default to 'M' if not provided

            # Update task fields
            task.contact = Contact.objects.get(id=contact_id)
            task.log = log_id
            task.task_date_time = task_date_time
            task.task_detail = task_detail
            task.created_by = assigned_by_user  # Or request.user for dynamic assignment
            task.tasktype = task_type

            # Save updated task
            task.save()

            serializer = TaskSerializer(task)
            return Response({"message": "Task updated successfully", "task": serializer.data}, status=status.HTTP_200_OK)

        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the task object
            task = Task.objects.get(id=id)

            if not task.is_active:
                return Response({"message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

            # Delete the task
            task.is_active = False
            task.save()

            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



