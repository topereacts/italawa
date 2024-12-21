from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['poster', 'name', 'category', 'start_time', 'end_time', 'description', 
                'undisclosed', 'location', 'directions', 'socials']