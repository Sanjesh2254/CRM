from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response

from lead.models import Contact
from lead.serializers.contactserializer import ContactSerializer
from lead.serializers.opportuinityserializer import OpportunitySerializer,PostOpportunitySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.leadserializer import PostLeadSerializer,  LeadSerializer,MarketSegmentSerializer,FocusSegmentSerializer,CountrySerializer,StateSerializer,EmpSerializer,TagSerializer, VerticalSerializer
from .models import Lead,Employee,Opportunity
from accounts.models import Market_Segment,Focus_Segment,Country,State,Tag,Vertical,Contact_Status,Lead_Source
from rest_framework.pagination import PageNumberPagination
from .serializers.contactserializer import LeadSourceSerializer,ContactStatusSerializer
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
        page_size = 10  
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
        
        elif dropdown_type=='vertical':
            verticals = Vertical.objects.all()
            serializer = VerticalSerializer(verticals, many=True)
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
        page_size = 10 # Default page size
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
        

from datetime import datetime
class ReportView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            body = request.data
            leads = Lead.objects.all()
            total_leads_count = leads.count()
            date = body.get('date')
            month = body.get('month')
            year = body.get('year')
            owner_id = body.get('owner_id')
            created_by = body.get('created_by')
            vertical_id = body.get('vertical_id')
            focus_segment = body.get('focus_segment')
            state = body.get('state')
            country = body.get('country')
            market_segment = body.get('market_segment')
            if date:
                try:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    leads = leads.filter(created_on=date_obj.date())
                except ValueError:
                        return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)
            elif month and year:
                try:
                    leads = leads.filter(created_on__year=year, created_on__month=month)
                except ValueError:
                    return Response({"error": "Invalid month/year format."}, status=status.HTTP_400_BAD_REQUEST)
            elif month and not year:
                try:
                    leads = leads.filter(created_on__month=month)
                except ValueError:
                    return Response({"error": "Invalid month/year format."}, status=status.HTTP_400_BAD_REQUEST)
            elif year:
                leads = leads.filter(created_on__year=year)

            # Apply filtering only for one field at a time
            elif owner_id:
                leads = leads.filter(lead_owner_id=owner_id)
            elif created_by:
                leads = leads.filter(created_by_id=created_by)
            elif vertical_id:
                leads = leads.filter(focus_segment__vertical_id=vertical_id)
            elif focus_segment:
                leads = leads.filter(focus_segment_id=focus_segment)
            elif state:
                leads = leads.filter(state_id=state)
            elif country:
                leads = leads.filter(country_id=country)
            elif market_segment:
                leads = leads.filter(market_segment_id=market_segment)

            # Count the filtered leads
            filtered_leads_count = leads.count()

            return JsonResponse({
                "total_leads_count": total_leads_count,
                "filtered_count": filtered_leads_count
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#--------------sumith--------


from .models import Task, Contact, Task_Assignment
from .serializers.taskserializer import TaskSerializer, GetTaskSerializer
from django.utils.timezone import now, timedelta
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
        
    

#-------------------VS-----------------------------
class Opportunity_create(APIView):
    def get(self,request):      
        opportunity = Opportunity.objects.all()
        serializer = OpportunitySerializer(opportunity, many=True)
        return Response(serializer.data)
    def post(self, request):
        data = request.data.copy()
        data.update(request.FILES)
        
        serializer = PostOpportunitySerializer(data=data) 
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Opportunity created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Opportunity_ById(APIView):
    def get(self, request, opportunity_id):
        opportunities = Opportunity.objects.filter(lead=opportunity_id)       
        if opportunities.exists():
            serializer = OpportunitySerializer(opportunities, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No opportunities found for this lead"}, status=status.HTTP_404_NOT_FOUND)

    def put(self,request,opportunity_id):
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
            serializer = OpportunitySerializer(opportunity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Opportunity updated", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Opportunity.DoesNotExist:
            return Response({"error": "Opportunity not found"}, status=status.HTTP_404_NOT_FOUND)
    def delete(self,request,opportunity_id):
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
            opportunity.is_active=False
            opportunity.save()
            return Response({"message":"opportunity deactivate"},status=status.HTTP_204_NO_CONTENT)
        except Opportunity.DoesNotExist:
            return Response({"error":"opportunity not found"},status=status.HTTP_404_NOT_FOUND)







#---------SANJESH-------------
class ContactView(APIView):

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, contact_id=None):
        if contact_id: # Retrieve a specific contact by 'contact_id'
            try:
                contact = Contact.objects.get(id=contact_id)
                serializer = ContactSerializer(contact)
                return Response(serializer.data)
            except Contact.DoesNotExist:
                return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            contacts = Contact.objects.all() # Retrieve all contacts if no 'id' is provided
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data)

    def put(self, request, contact_id=None):
        if contact_id: # Check if 'id' is provided
            try:
                contact = Contact.objects.get(id=contact_id)
                serializer = ContactSerializer(contact, data=request.data, partial=True) # Allow partial updates
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Contact.DoesNotExist:
                return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "ID not provided"}, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request,contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.is_active=False
            contact.save()
            return Response({"message": "Contact deactivate"}, status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)

class Contactdropdownlistview(APIView):
    def get(self, request):
        dropdown_type = request.query_params.get('type')

        if dropdown_type == 'contactstatus':
            contact_status = Contact_Status.objects.all()
            serializer = ContactStatusSerializer(contact_status, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif dropdown_type == 'lead_source':
            source = Lead_Source.objects.all()
            serializer = LeadSourceSerializer(source, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid dropdown type'}, status=status.HTTP_400_BAD_REQUEST)










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