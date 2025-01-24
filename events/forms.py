from django import forms
from django.contrib.auth import get_user_model


class paymentForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)



User = get_user_model()

class StaffForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'phone']