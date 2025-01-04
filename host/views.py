from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.http import JsonResponse, QueryDict, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import json



# Create your views here.
from .forms import EventForm, TicketForm
from .models import Event, Ticket
from events.models import Order

@csrf_exempt
@login_required  
def index(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            if not event.poster:
                event.poster = 'path/to/default/image.jpg'
            event.save()
            return JsonResponse({
                'success': True,
                'id': event.id,
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
        return render(request, "host/index.html", {'form': form})



def get_user_events(request):
    if request.user.is_authenticated:
        events = Event.objects.filter(created_by=request.user)
        events_data = [{
            'id': event.id,
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


# @csrf_exempt
# @login_required
# def manage_event(request, event_id):
#     print("View reached")  # Debugging line
#     event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
#     if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         event_data = {
#             'id': event.id,
#             'name': event.name,
#             'category': event.category,
#             'start_time': event.start_time,
#             'end_time': event.end_time,
#             'description': event.description,
#             'location': event.location,
#             'undisclosed': event.undisclosed,
#             'directions': event.directions,
#             'socials': event.socials,
#             'poster': event.poster.url if event.poster else None
#         }
#         return JsonResponse(event_data)
    
#     if request.method == 'POST' or request.method == 'PUT':
#         print("Handling POST/PUT request")  # Debugging line
#         print("Request POST data:", request.POST)  # Debugging line
#         try:
#             data = request.POST
#             event.name = data.get('name')
#             print(f"Event name: {event.name}")
#             event.category = data.get('category')
#             event.start_time = data.get('start_time')
#             event.end_time = data.get('end_time')
#             event.description = data.get('description')
#             event.location = data.get('location')
#             event.undisclosed = data.get('undisclosed')
#             event.directions = data.get('directions')
#             event.socials = data.get('socials')

#             if 'poster' in request.FILES:
#                 event.poster = request.FILES['poster']
#                 print("Poster file received")  # Debugging line
#             else:
#                 print("No poster file received")
#             event.save()
#             print("Event saved successfully")  # Debugging line
#             return JsonResponse({'success': True, 
#                                 'id': event.id, 
#                                 'name': event.name,
#                                 'category': event.category,
#                                 'start_time': event.start_time,
#                                 'end_time': event.end_time,
#                                 'description': event.description,
#                                 'location': event.location,
#                                 'undisclosed': event.undisclosed,
#                                 'directions': event.directions,
#                                 'socials': event.socials,
#                                 'poster': event.poster.url if event.poster else None
#                             })
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
#     return render(request, 'host/manage_event.html', {'event': event})



@csrf_exempt
@login_required
def manage_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': event.id,
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
        }
        return JsonResponse(data)
    
    elif request.method == 'POST':
        # Update event details
        event.name = request.POST.get('name')
        event.category = request.POST.get('category')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if start_time:
            event.start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))

        if end_time:
            event.end_time = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%dT%H:%M'))

        event.description = request.POST.get('description')
        event.location = request.POST.get('location')
        event.undisclosed = request.POST.get('undisclosed', False)
        event.directions = request.POST.get('directions')
        event.socials = request.POST.get('socials')
        
        # Handle poster update if a new file is uploaded
        if 'poster' in request.FILES:
            event.poster = request.FILES['poster']
        
        # Save the updated event
        event.save()
        return JsonResponse({'message': 'Event updated successfully',
                            'success': True, 
                            'id': event.id,
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
    # Fetch related orders
    orders = Order.objects.filter(ticket__event=event).order_by('-created_at')

    return render(request, 'host/manage_event.html', {'event': event, 'orders': orders})


@csrf_exempt
@login_required
def tickets(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    tickets = Ticket.objects.filter(event=event)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.save()
            return JsonResponse({
                'success': True,
                'event_id': event.id,
                'type': ticket.type,
                'price': ticket.price,
                'quantity': ticket.quantity,
                'description': ticket.description,
                'deadline': ticket.deadline
            })
        else:
            print("Form errors:", form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TicketForm()
    return render(request, "host/ticket.html", {'event': event, 'tickets': tickets, 'form': form})