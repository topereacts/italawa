import os
import json
import barcode
import uuid
from barcode.writer import ImageWriter
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Min
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.
from .forms import paymentForm
from .models import User, Order, TicketInstance
from host.models import Event, Ticket, Staff # Adjust the import based on your app name



def index(request):
    current_time = timezone.now()  # Get the current datetime
    events = Event.objects.annotate(min_price=Min('ticket__price')).exclude(end_time__lt=current_time)
    return render(request, "events/index.html", {
        'events': events,
    })


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            staff_member = Staff.objects.filter(user=user).first()
            if staff_member and staff_member.role == 'staff':
                event_id = staff_member.event.id
                return redirect("host:manage_event", event_id=event_id)
            else:
                return redirect("host:index")
        else:
            return render(request, "events/login.html", {
                "message": "Invalid credentials."
            })
    return render(request, "events/login.html")

def logout_view(request):
    logout(request)
    return redirect("event:index")




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
        return HttpResponseRedirect(reverse("event:login"))
    else:
        return render(request, "events/register.html")


def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)  # Fetch the specific event
    return render(request, "events/event_detail.html", {
        'event': event,
    })


@csrf_exempt
def get_tickets(request, event_id):
    tickets = Ticket.objects.filter(event_id=event_id)
    tickets_data = [
        {
            'id': ticket.id,
            'type': ticket.type,
            'price': ticket.price,
            'quantity': ticket.quantity,
            'description': ticket.description,
            'deadline': ticket.deadline,
        }
        for ticket in tickets
    ]
    return JsonResponse({'tickets': tickets_data})


@csrf_exempt
def events_page(request):
    query = request.GET.get('q')  
    current_time = timezone.now()  
    events = Event.objects.annotate(min_price=Min('ticket__price')).exclude(end_time__lt=current_time)

    # Retrieve filter parameters
    category = request.GET.get('category', '')
    # Retrieve filter parameters
    price = request.GET.get('price', '')

    # Filter by ticket price
    if price:
        events = events.filter(id__in=Ticket.objects.filter(price__lte=float(price)).values_list('event_id', flat=True))
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    location = request.GET.get('location', '')

    # Apply filters
    if category:
        events = events.filter(category=category)
    if start_date:
        events = events.filter(start_time__gte=start_date)
    if end_date:
        events = events.filter(end_time__lte=end_date)
    if location:
        events = events.filter(location__icontains=location)

    if query:
        # Filter events by name or description containing the query
        events = events.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Ensure consistent ordering
    events = events.order_by('start_time')  # Replace 'start_time' with the field you prefer for ordering

    paginator = Paginator(events, 8)  # 8 events per page
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)

    context = {
        'events': events,
        'query': query,
        'categories': Event.objects.values_list('category', flat=True).distinct(),
    }


    return render(request, 'events/events_page.html', context)



@csrf_exempt
def save_order(request, event_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        tickets_purchased = []
        total_amount = 0
        orders = []

        # Group tickets by type
        ticket_groups = {}
        for ticket_item in data['tickets']:
            ticket_id = ticket_item['ticket_id']
            if ticket_id not in ticket_groups:
                ticket_groups[ticket_id] = {
                    'ticket': Ticket.objects.get(id=ticket_id),
                    'quantity': 0,
                    'price': ticket_item['price']
                }
            ticket_groups[ticket_id]['quantity'] += ticket_item['quantity']

        # Create an order for each ticket type
        for ticket_id, details in ticket_groups.items():
            ticket = details['ticket']
            quantity = details['quantity']
            price = details['price'] * quantity

            # Generate a unique order ID for group
            unique_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            # Create the order and save the unique order ID
            order = Order.objects.create(
                ticket=ticket,
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                quantity=quantity,
                unique_order_id=unique_order_id
            )
            orders.append(order)

            # Update ticket quantities and sales
            ticket.tickets_sold += quantity
            ticket.quantity -= quantity
            ticket.save()

            # Generate barcodes for each individual ticket in the order
            for i in range(quantity):
                ticket_unique_order_id = f"{unique_order_id}-{i+1}"  # Unique barcode per ticket

                TicketInstance.objects.create(
                    order=order,
                    ticket_unique_order_id=ticket_unique_order_id
                )

                # Generate barcode image
                barcode_path = os.path.join(settings.MEDIA_ROOT, f"barcodes/order_{ticket_unique_order_id}.png")
                os.makedirs(os.path.dirname(barcode_path), exist_ok=True)
                barcode_generator = barcode.get('code128', ticket_unique_order_id, writer=ImageWriter())
                barcode_generator.save(barcode_path.replace('.png', ''))

                # Append ticket details (adjusting for quantity in the response)
                tickets_purchased.append({
                    'type': ticket.type,
                    'description': ticket.description,
                    'unique_order_id': ticket_unique_order_id,
                    'quantity': 1,  # Each individual ticket gets quantity of 1
                    'price': details['price'],
                    'barcode_url': f"{settings.MEDIA_URL}barcodes/order_{ticket_unique_order_id}.png"
                })

            total_amount += price

        # Update event revenue
        event = ticket.event
        event.revenue += total_amount
        event.save()

        return JsonResponse({
            'full_name': data['full_name'],
            'email': data['email'],
            'phone': data['phone'],
            'tickets': tickets_purchased,
            'total_amount': total_amount,
            'orders': len(orders)
        })