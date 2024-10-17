from django.urls import path
from .views import *

urlpatterns = [
    path('contacts/create/',Contact_Create.as_view(), name='contact-create'),
    path('contacts/Delete/<int:pk>/',Contact_Delete.as_view(), name='contact-delete'),
    path('contacts/Update/<int:pk>/',Contact_Update.as_view(), name='contact-update'),
 
]