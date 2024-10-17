from rest_framework.response import Response
from rest_framework import status
from ..serializers.leadserializer import leadSerializer,marketSegmentSerializer,focusSegmentSerializer,countrySerializer,stateSerializer
from ..models import Lead
from accounts.models import Market_Segment,Focus_Segment,Country,State

def create_lead(request):
    serializer = leadSerializer(data=request.data) 
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Lead Created Successfully!","data":serializer.data},status=status.HTTP_201_CREATED)
    return Response ({'errors':serializer.errors},status=status.HTTP_400_BAD_REQUEST)


def delete_lead(request,lead_id):
    try:
        lead= Lead.objects.get(id=lead_id)
        lead.delete()
        return Response({"message":"Lead permanently deleted!"},status=status.HTTP_204_NO_CONTENT)
    except Lead.DoesNotExist:
        return Response({"error":"Lead not found"},status=status.HTTP_404_NOT_FOUND)
    
def deactivate_lead(request,lead_id):
    try:
        lead=Lead.objects.get(id=lead_id)
        lead.is_active=False
        lead.save()
        return Response({"message": "Lead deactivated!"}, status=status.HTTP_200_OK)
    except Lead.DoesNotExist:
        return Response({"error":"Lead not found"},status=status.HTTP_404_NOT_FOUND)
    
def update_lead(request,lead_id):
    try:
        lead=Lead.objects.get(id=lead_id)
        serializer = leadSerializer(lead, data=request.data, partial=True)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"message":"Lead Updated Successfully!","data":serializer.data},status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Lead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)

def market_segment_list(request):
    market_segments=Market_Segment.objects.all()
    serializer=marketSegmentSerializer(market_segments,many=True)
    return Response(serializer.data)

def focus_segment_list(request):
    focus_segments=Focus_Segment.objects.all()
    serializer=focusSegmentSerializer(focus_segments,many=True)
    return Response(serializer.data)

def country_list(request):
    countries=Country.objects.all()
    serializer=countrySerializer(countries,many=True)
    return Response(serializer.data)

def state_list(request,country_id):
    states=State.objects.filter(country=country_id)
    serializer=stateSerializer(states,many=True)
    return Response(serializer.data)