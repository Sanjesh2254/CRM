from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response

from lead.models import Contact
from lead.serializers import ContactSerializer

    

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

    def delete(self, request, pk):
        try:
            contact = Contact.objects.get(pk=pk)
            contact.is_active=False
            contact.save()
            return Response({"message": "Contact permanently deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)
        
    # def put(self,request, pk):
    #  try:
    #     contact = Contact.objects.get(pk=pk)
    #     contact.is_active=False
    #     contact.save()
    #     return Response({"message":"contact deactivate"},status=status.HTTP_204_NO_CONTENT)
    #  except Contact.DoesNotExist:
    #     return Response({"error":"contact not found"},status=status.HTTP_404_NOT_FOUND)
     

class Contact_Update(APIView): 
  
 def put(self,request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
        serializer = ContactSerializer(contact, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Contact.DoesNotExist:
        return Response({"error": "Contact not found"}, status=status.HTTP_404_NOT_FOUND)