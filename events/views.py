from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
from .forms import EventForm
from .models import User, Event

def index(request):
    return render(request, "events/index.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("create_event"))
        else:
            return render(request, "events/login.html", {
                "message": "Invalid credentials."
            })
    return render(request, "events/login.html")

def logout_view(request):
    logout(request)
    return render(request, "events/login.html", {
        "message": "Logout successfull"
    })


# def send_welcome_email(user_email):
#     send_mail(
#         'Welcome to My Site',
#         'Thank you for registering.',
#         'jessiecolter8@gmail.com',
#         [user_email],
#         fail_silently=False,
#     )


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        creator = request.POST["creator"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "events/register.html", {
                "message": "Passwords must match."
            })
        try:
            if User.objects.filter(email=email).exists():
                return render(request, "events/register.html", {
                    "message": "Email already exists."
                })
            user = User.objects.create_user(username=email, email=email, password=password)
            user.name = name  
            user.creator = creator
            user.phone = phone
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "events/register.html", {
                "message": "User already exists."
            })
        # send_welcome_email(user.email)
        return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "events/register.html")


@csrf_exempt
@login_required  
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return JsonResponse({
                'success': True,
                'name': event.name,
                'category': event.category,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'description': event.description,
                'location': event.location,
                'undisclosed': event.undisclosed,
                'directions': event.directions,
                'socials': event.socials,
                'poster': event.poster.url if event.poster else None
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EventForm()
        return render(request, "events/create_event.html", {'form': form})



def get_user_events(request):
    if request.user.is_authenticated:
        events = Event.objects.filter(created_by=request.user)
        events_data = [{
            'name': event.name,
            'category': event.category,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'description': event.description,
            'location': event.location,
            'undisclosed': event.undisclosed,
            'directions': event.directions,
            'socials': event.socials,
            'poster': event.poster.url if event.poster else None
        } for event in events]
        return JsonResponse(events_data, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
