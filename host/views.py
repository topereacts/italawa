from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.http import JsonResponse, QueryDict, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Sum
from datetime import datetime
import json



# Create your views here.
from .forms import EventForm, TicketForm
from .models import Event, Ticket, Staff, Event
from events.models import Order, TicketInstance, User
from events.forms import StaffForm

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



@csrf_exempt
@login_required
def manage_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not Staff.objects.filter(user=request.user, event=event).exists():
        return HttpResponseForbidden("You do not have permission to access this event.")
    
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
    
    # Calculate total order quantity
    total_quantity = orders.aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'host/manage_event.html', {
        'event': event, 
        'orders': orders,
        'total_quantity': total_quantity
    })


@csrf_exempt
@login_required
def tickets(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not Staff.objects.filter(user=request.user, event=event).exists():
        return HttpResponseForbidden("You do not have permission to access this event.")    
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

@csrf_exempt
@login_required
def revenue(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    return render(request, "host/revenue.html", {
        'event': event,
    })

@csrf_exempt
@login_required
def scan_ticket_page(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.created_by != request.user and not Staff.objects.filter(user=request.user, event=event).exists():
        return HttpResponseForbidden("You do not have permission to access this event.")  
    scanned_tickets = TicketInstance.objects.filter(order__ticket__event=event, is_checked_in=True)

    ticket_data = [
        {
            'order_id': ticket.order.id,
            'ticket_unique_order_id': ticket.ticket_unique_order_id,
            'checked_in_at': ticket.checked_in_at.strftime('%Y-%m-%d %H:%M:%S'),
            'ticket_type': ticket.order.ticket.type,
            'ticket_price': ticket.order.ticket.price,
            'ticket_description': ticket.order.ticket.description,
        }
        for ticket in scanned_tickets
    ]
 
    return render(request, 'host/scan_ticket.html', {
        'event': event,
        'scanned_tickets': ticket_data
    })

@csrf_exempt
@login_required
def check_in_ticket(request):
    ticket_unique_order_id = request.GET.get('ticket_unique_order_id')
    ticket_instance = get_object_or_404(TicketInstance, ticket_unique_order_id=ticket_unique_order_id)
    
    if ticket_instance.is_checked_in:
        # If the ticket is already checked in, return an error response
        return JsonResponse({'status': 'error', 'message': 'Ticket already checked in'})
    
    # Mark the ticket as checked in
    ticket_instance.is_checked_in = True
    ticket_instance.checked_in_at = timezone.now()
    ticket_instance.save()

    # Fetch the related ticket details
    ticket = ticket_instance.order.ticket

    return JsonResponse({'status': 'success', 'ticket_details': {
        'order_id': ticket_instance.order.id,
        'ticket_unique_order_id': ticket_instance.ticket_unique_order_id,
        'checked_in_at': ticket_instance.checked_in_at.strftime('%Y-%m-%d %H:%M:%S'),
        'ticket_type': ticket.type,
        'ticket_price': ticket.price,
        'ticket_description': ticket.description,
    }})






@csrf_exempt
@login_required
def create_staff(request, event_id):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            print(f"Creating user with username: {user.username}")  # Debugging statement
            user.set_password('italawa')  # Set a default password or generate one
            try:
                user.save()
            except IntegrityError as e:
                print(f"IntegrityError: {e}")  # Debugging statement
                form.add_error(None, "Username already exists.")
                event = Event.objects.get(id=event_id)
                staff_list = Staff.objects.filter(event=event)
                return render(request, 'host/staff_mgmt.html', {
                    'form': form, 
                    'staff_list': staff_list,
                    'event': event
                })
            event = Event.objects.get(id=event_id)
            Staff.objects.create(user=user, event=event, role='staff')
            return redirect('host:manage_event', event_id=event_id)
    else:
        form = StaffForm()
    
    event = Event.objects.get(id=event_id)
    staff_list = Staff.objects.filter(event=event)
    return render(request, 'host/staff_mgmt.html', {
        'form': form, 
        'staff_list': staff_list,
        'event': event
    })

@csrf_exempt
@login_required
def profile(request):
    user =  get_object_or_404(User, id=request.user.id)
    return render(request, 'host/profile.html', {
        'user': user
    })

@csrf_exempt
@login_required
def remove_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    event_id = staff.event.id  # Assuming staff is related to an event
    staff.delete()
    return redirect('host:staff_mgmt', event_id=event_id)
    