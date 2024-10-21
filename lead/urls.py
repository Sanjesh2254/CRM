from django.urls import path
from .views import *

urlpatterns = [

    #LEAD LIST
    #-by_SABARIGIRIVASAN
    path('leaddetails/', LeadView.as_view(),name='lead_details'),              
    path('leaddetails/<int:lead_id>/', LeadView.as_view(),name='lead_details_by_id'),
    path('dropdown/', DropdownListView.as_view(),name='drop_down'),                   
    path('dropdown/state/<int:country_id>/', DropdownListView.as_view(),name='state_drop_down'),
    #-by_SANKARMAHARAJAN
    path('filter_lead/', LeadFilterView.as_view(), name='lead-filter'),

    # *******Sanjesh*******
    path('contacts/create/',Contact_Create.as_view(), name='contact-create'),
    path('contacts/Delete/<int:contact_id>/',Contact_Delete.as_view(), name='contact-delete'),
    path('contacts/Update/<int:contact_id>/',Contact_Update.as_view(), name='contact-update'),
    # ********Afsal********
     path('employees/', EmployeeListView.as_view()),  # Employee dropdown API
    path('lead/<int:lead_id>/assign/', LeadAssignmentView.as_view()),  # Lead assignment API
    path('contact/<int:contact_id>/', ContactDetailView.as_view()),  # API for retrieving a specific 
    path('log/<int:id>/', LogManagement.as_view(), name='LogManagement'), # API for Creating, Editing, Deleting Log and Task
    path('log_stages/', LogStageListView.as_view(), name='log-stage-list'),  # Log Stages Dropdown API
    path('leadlog/<int:lead_id>/', logsbyLeadsView.as_view(), name='log-stage-list'),  # API for all the Logs under a Lead
    path('contactlog/<int:contact_id>/', logsbyContactView.as_view(), name='log-stage-list'),  # API for all the Logs under a Contact



]