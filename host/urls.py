from django.urls import path

from . import views

app_name = 'host'


urlpatterns = [
    path("", views.index, name="index"),
    path('api/events', views.get_user_events, name='get_user_events'),
    path('profile/', views.profile, name='profile'),
    path('manage_event/<int:event_id>/', views.manage_event, name='manage_event'),
    path('manage_event/<int:event_id>/tickets/', views.tickets, name='tickets'),
    path('manage_event/<int:event_id>/revenue', views.revenue, name='revenue'),
    path('manage_event/<int:event_id>/scan_ticket', views.scan_ticket_page, name='scan_ticket_page'),
    path('check_in_ticket/', views.check_in_ticket, name='check_in_ticket'),
    path('manage_event/<int:event_id>/staff_mgmt', views.create_staff, name='staff_mgmt'),
    path('remove_staff/<int:staff_id>/', views.remove_staff, name='remove_staff'),
] 