from django.urls import path

from . import views

app_name = 'event'


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("event_detail/<int:event_id>", views.event_detail, name="event_detail"),
    path('event_detail/<int:event_id>/get_tickets/', views.get_tickets, name='get_tickets'),
    path('event_detail/<int:event_id>/save_order/', views.save_order, name='save_order'),
    path('events_page', views.events_page, name="events_page"),
] 