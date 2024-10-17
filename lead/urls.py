from django.urls import path
from .views import *

urlpatterns = [
    # *******Sanjesh*******
    path('contacts/create/',Contact_Create.as_view(), name='contact-create'),
    path('contacts/Delete/<int:pk>/',Contact_Delete.as_view(), name='contact-delete'),
    path('contacts/Update/<int:pk>/',Contact_Update.as_view(), name='contact-update'),
    # ********Afsal********
    path('employees/', EmployeeListView.as_view()),  # Employee dropdown API
    path('lead/<int:lead_id>/assign/', LeadAssignmentView.as_view()),  # Lead assignment API
    path('contact/<int:contact_id>/', ContactDetailView.as_view()),  # API for retrieving a specific contact
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