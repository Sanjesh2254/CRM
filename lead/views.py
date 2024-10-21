from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response

from lead.models import Contact
from lead.serializers.contactserializer import ContactSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.leadserializer import PostLeadSerializer,  LeadSerializer,MarketSegmentSerializer,FocusSegmentSerializer,CountrySerializer,StateSerializer,EmpSerializer,TagSerializer
from .models import Lead,Employee
from accounts.models import Market_Segment,Focus_Segment,Country,State,Tag
from rest_framework.pagination import PageNumberPagination
#Lead Details


class LeadView(APIView):
    def post(self, request):
        serializer = PostLeadSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Lead Created Successfully!","data":serializer.data},status=status.HTTP_201_CREATED)
        return Response ({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, lead_id=None):
        if lead_id:
            try:
                lead=Lead.objects.get(id=lead_id)
                serializer = LeadSerializer(lead, data=request.data, partial=True)
                if(serializer.is_valid()):
                    serializer.save()
                    return Response({"message":"Lead Updated Successfully!","data":serializer.data},status=status.HTTP_200_OK)
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'lead_id is required for update'}, status=status.HTTP_400_BAD_REQUEST)


    
    def delete(self, request, lead_id=None):
        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id)
                lead.is_active = False  # Soft-delete (deactivation)
                lead.save()
                return Response({"message": "Lead deactivated!"}, status=status.HTTP_200_OK)
            except Lead.DoesNotExist:
                return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'lead_id is required for deactivation'}, status=status.HTTP_400_BAD_REQUEST)
    
    class LeadPagination(PageNumberPagination):
        page_size = 20  
        page_size_query_param = 'page_size'
        max_page_size = 1000

    def get(self, request, lead_id=None):
        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id)
                serializer = LeadSerializer(lead)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Lead.DoesNotExist:
                return Response({'error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Filter active leads and order by latest created
            leads = Lead.objects.filter(is_active=True).order_by('-created_on', '-id')
            
            # Apply pagination using query parameters
            paginator = self.LeadPagination()
            result_page = paginator.paginate_queryset(leads, request)
            
            # Return paginated response
            return paginator.get_paginated_response(LeadSerializer(result_page, many=True).data)
        



class DropdownListView(APIView):

    def get(self, request, country_id=None):
        dropdown_type = request.query_params.get('type')

        if dropdown_type == 'market_segment':
            market_segments=Market_Segment.objects.all()
            serializer=MarketSegmentSerializer(market_segments,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'focus_segment':
            focus_segments=Focus_Segment.objects.all()
            serializer=FocusSegmentSerializer(focus_segments,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'country':
            countries=Country.objects.all()
            serializer=CountrySerializer(countries,many=True)
            return Response(serializer.data)
        elif dropdown_type == 'state' and country_id:
            states=State.objects.filter(country=country_id)
            serializer=StateSerializer(states,many=True)
            return Response(serializer.data)
        elif dropdown_type =='tags':
            tags=Tag.objects.all()
            serializer=TagSerializer(tags,many=True)
            return Response(serializer.data)
        
        elif dropdown_type == 'owner':
            designations = ['BDE', 'BDM', 'Admin']
            employees = Employee.objects.filter(designation__designation__in=designations, is_active=True)
            serializer = EmpSerializer(employees, many=True)
            return Response(serializer.data)
        
        elif dropdown_type=='created_by':
            employees = Employee.objects.all()
            serializer = EmpSerializer(employees, many=True)
            return Response(serializer.data)
        

        else:
            return Response({'error': 'Invalid dropdown type or missing parameters.'}, status=status.HTTP_400_BAD_REQUEST)

from django.http import JsonResponse
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import status
from .models import Lead

class LeadFilterView(APIView):

    class LeadPagination(PageNumberPagination):
        page_size = 20 # Default page size
        page_size_query_param = 'page_size'
        max_page_size = 1000  # You can set a maximum limit for page size

    def post(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def get(self, request, *args, **kwargs):
        return self.filter_and_paginate(request)

    def filter_and_paginate(self, request):
        try:
            # Load the body as JSON
            body = request.data if request.method == 'POST' else request.query_params

            # Start by querying all leads
            leads = Lead.objects.all()

            # Apply filters based on the request body or query parameters
            vertical_ids = body.get('vertical_id', [])
            if vertical_ids:
                leads = leads.filter(focus_segment__vertical__id__in=vertical_ids)

            focus_segment_ids = body.get('focus_segment', [])
            if focus_segment_ids:
                leads = leads.filter(focus_segment__id__in=focus_segment_ids)

            market_segment_ids = body.get('market_segment', [])
            if market_segment_ids:
                leads = leads.filter(market_segment__id__in=market_segment_ids)

            state_ids = body.get('state_id', [])
            if state_ids:
                leads = leads.filter(state__id__in=state_ids)

            country_ids = body.get('country_id', [])
            if country_ids:
                leads = leads.filter(country__id__in=country_ids)

            created_on_dates = body.get('created_on', [])
            if created_on_dates:
                leads = leads.filter(created_on__in=created_on_dates)

            annual_revenue_range = body.get('annual_revenue', [])
            if len(annual_revenue_range) == 2:
                min_revenue, max_revenue = annual_revenue_range
                leads = leads.filter(annual_revenue__gte=min_revenue, annual_revenue__lte=max_revenue)

            # Handle pagination
            paginator = self.LeadPagination()
            leads_page = paginator.paginate_queryset(leads, request)

            # Prepare the response data
            lead_data = [
                {
                    "id": lead.id,
                    "name": lead.name,
                    "focus_segment": {
                        "id": lead.focus_segment.id,
                        "focus_segment": lead.focus_segment.focus_segment
                    },
                    "vertical": {
                        "id": lead.focus_segment.vertical.id,
                        "vertical": lead.focus_segment.vertical.vertical
                    },
                    "market_segment": {
                        "id": lead.market_segment.id,
                        "market_segment": lead.market_segment.market_segment
                    },
                    "state": {
                        "id": lead.state.id if lead.state else None,
                        "state_name": lead.state.state_name if lead.state else None
                    },
                    "country": {
                        "id": lead.country.id,
                        "country_name": lead.country.country_name
                    },
                    "created_on": lead.created_on,
                    "annual_revenue": lead.annual_revenue,
                    "company_number": lead.company_number,
                    "company_email": lead.company_email,
                    "company_website": lead.company_website,
                    "fax": lead.fax,
                    "tags": [{"id": tag.id, "tag": tag.tag} for tag in lead.tags.all()],
                    "lead_owner": {
                        "id": lead.lead_owner.id,
                        "username": lead.lead_owner.username
                    },
                    "created_by": {
                        "id": lead.created_by.id,
                        "username": lead.created_by.username
                    },
                    "is_active": lead.is_active,
                }
                for lead in leads_page
            ]

            # Return the filtered and paginated lead data with pagination links
            return paginator.get_paginated_response(lead_data)

        except Exception as e:
            # Return error response in case of an issue
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








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
from .serializers.logserializer import LogCreateUpdateSerializer, LogReadSerializer
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
        log_serializer = LogCreateUpdateSerializer(data=log_data)
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
        log_serializer = LogCreateUpdateSerializer(log, data=data, partial=True)

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

            log_serializer = LogReadSerializer(logs, many=True)
            return JsonResponse(log_serializer.data, safe = False, status=200)
        except Contact.DoesNotExist:
            return JsonResponse({'message': 'No contacts found for this lead'}, status = 404)

#calling all the logs of a Contact
class logsbyContactView(APIView):
    def get(self, request, contact_id):
        try:
            logs = Log.objects.filter(contact_id=contact_id, is_active = True)
            log_serializer =  LogReadSerializer(logs, many=True)
            return JsonResponse(log_serializer.data, safe=False, status=200)
        except Log.DoesNotExist:
            return JsonResponse({'message': 'Log does not exist'}, status =404)