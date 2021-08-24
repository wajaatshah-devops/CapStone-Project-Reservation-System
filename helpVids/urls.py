from django.urls import path, include
from .import views

app_name = 'helpVids'

urlpatterns = [
    path('help/', views.help_view, name='help'),
    path('staffHelp/', views.staff_help_view, name='staffHelp'),
]