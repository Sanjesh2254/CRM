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

    def put(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk)
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
  
 def post(self,request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
        serializer = ContactSerializer(contact, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Contact.DoesNotExist:
        return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
    










    # ***********Afsal******
    
from .functions.employee_list import get_employee_list
from .functions.lead_assignment import post_lead_assignment
from .functions.contact_detail import get_contact_detail
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
