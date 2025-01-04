from django import forms
from .models import Event, Ticket


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['poster', 'name', 'category', 'start_time', 'end_time', 'description', 
                'undisclosed', 'location', 'directions', 'socials']
        


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['type', 'price', 'quantity', 'description', 'deadline']