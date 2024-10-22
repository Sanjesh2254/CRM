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
    path('report_lead/',ReportView.as_view(),name='report_leads'),

    # *******Sanjesh*******
    path('contactdetails/', ContactView.as_view(),name='contact_details'), # For creating and listing all contacts
    path('contactdetails/<int:contact_id>/', ContactView.as_view(),name='contact_details_by_id'),
     path('contact-dropdown/', Contactdropdownlistview.as_view(), name='contact-dropdown'),


    # ********Afsal********
     path('employees/', EmployeeListView.as_view()),  # Employee dropdown API
    path('lead/<int:lead_id>/assign/', LeadAssignmentView.as_view()),  # Lead assignment API
    path('contact/<int:contact_id>/', ContactDetailView.as_view()),  # API for retrieving a specific 
    path('log/<int:id>/', LogManagement.as_view(), name='LogManagement'), # API for Creating, Editing, Deleting Log and Task
    path('log_stages/', LogStageListView.as_view(), name='log-stage-list'),  # Log Stages Dropdown API
    path('leadlog/<int:lead_id>/', logsbyLeadsView.as_view(), name='log-stage-list'),  # API for all the Logs under a Lead
    path('contactlog/<int:contact_id>/', logsbyContactView.as_view(), name='log-stage-list'),  # API for all the Logs under a Contact


 #-----------Sumith---------------
    path('create-task/', CreateTaskView.as_view(), name='create-task'),
    path('task/<int:id>/', TaskManagement.as_view(), name='task'),


#---------vs-------------
    path('opportunity/',Opportunity_create.as_view(), name="Opportunity_create"),
    path('opportunity/<int:opportunity_id>/',Opportunity_ById.as_view(), name="Opportunity_ById"),

]