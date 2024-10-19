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
from .models import Log_Stage, Log, Task
from django.contrib.auth.models import User
from .serializers.logserializer import LogSerializer
from .serializers.taskserializer import TaskSerializer
from .functions.employee_list import get_employee_list
from .functions.lead_assignment import post_lead_assignment
from .functions.contact_detail import get_contact_detail
from .functions.log_stage_list import get_log_stages
from .functions.logs_by_lead import get_logs_by_lead
from .functions.logs_by_contact import get_logs_by_contact



# Employee List View
class EmployeeListView(APIView):
    def get(self, request):
        return get_employee_list(request)

# Lead Assignment View
class LeadAssignmentView(APIView):
    def post(self, request, lead_id):
        return post_lead_assignment(request, lead_id)
    
# Call the function to get contact detail
class ContactDetailView(APIView):
    def get(self, request, contact_id):
        return get_contact_detail(contact_id)

# Creating, Editing, Deleting Log and Task
class LogManagement(APIView):
    
    # Create Log and Task
    def post(self, request, id):
        try:
            contact = Contact.objects.get(id=id)
            lead = contact.lead  # Get the related lead to retrieve focus_segment
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'Contact not found'}, status=404)

        try:
            data = request.data
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data'}, status=400)

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

#***********************************************************************************

# Calling log_status for creating Log
class LogStageListView(APIView):
    def get(self, request):
        return get_log_stages(request)

#Calling all the logs in a Lead
class logsbyLeadsView(APIView):
    def get(self, request, lead_id):
        return get_logs_by_lead(request, lead_id)

#calling all the logs of a Contact
class logsbyContactsView(APIView):
    def get(self, request, contact_id):
        return get_logs_by_contact(request, contact_id)
    

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
