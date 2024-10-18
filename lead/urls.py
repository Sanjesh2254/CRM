from django.urls import path
from .views import *

urlpatterns = [
    # *******Sanjesh*******
    path('contacts/create/',Contact_Create.as_view(), name='contact-create'),
    path('contacts/Delete/<int:contact_id>/',Contact_Delete.as_view(), name='contact-delete'),
    path('contacts/Update/<int:contact_id>/',Contact_Update.as_view(), name='contact-update'),
    # ********Afsal********
    path('employees/', EmployeeListView.as_view()),  # Employee dropdown API
    path('lead/<int:lead_id>/assign/', LeadAssignmentView.as_view()),  # Lead assignment API
    path('contact/<int:contact_id>/', ContactDetailView.as_view()),  # API for retrieving a specific contact 
    path('log/create/<int:contact_id>/', LogCreateView.as_view(), name='log-create'), # API for creating a Log
    path('log/edit/<int:log_id>/', LogEditView.as_view(), name='log-edit'),  # API for editing Log and Task
    path('log/delete/<int:log_id>/', LogDeleteView.as_view(), name='log-delete'),  # API for deleting Log and Task
     path('log_stages/', LogStageListView.as_view(), name='log-stage-list'),  # Log Stages Dropdown API
    #--------sankar----
     path('filter/leads/', leadfilterView.as_view(), name='lead-filter'),
     #------sabari-----
     path('create/', create.as_view(), name='create_lead'),
   # path('permanent_delete/<int:lead_id>/', permanent_delete.as_view(), name='delete_lead'),
    path('delete/<int:lead_id>/', delete.as_view(), name='delete_lead'),
    path('update/<int:lead_id>/', update.as_view(), name='update_lead'),
    path('focus_segment_list/',focus_segment_list_view.as_view(),name='focus_segments'),
    path('market_segment_list/',market_segment_list_view.as_view(),name='market_segments'),
    path('country_list/',country_list_view.as_view(),name='countries'),
    path('state_list/<int:country_id>/',state_list_view.as_view(),name='states')

]