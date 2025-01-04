from django.urls import path

from . import views

app_name = 'host'


urlpatterns = [
    path("", views.index, name="index"),
    path('api/events', views.get_user_events, name='get_user_events'),
    path('manage_event/<int:event_id>/', views.manage_event, name='manage_event'),
    path('manage_event/<int:event_id>/tickets/', views.tickets, name='tickets'),
] 