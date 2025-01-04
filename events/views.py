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
from .models import User, Order
from host.models import Event, Ticket  # Adjust the import based on your app name



def index(request):
    today = timezone.now().date()  # Get the current date
    events = Event.objects.annotate(min_price=Min('ticket__price')).exclude(end_time__date=today)
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
            return redirect("host:index")  # Specify the app name
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



def events_page(request):
    categories = Event.objects.values_list('category', flat=True).distinct()
    events = Event.objects.annotate(min_price=Min('ticket__price'))

    location = request.GET.get('location')
    if location:
        events = events.filter(location__icontains=location)

    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        events = events.filter(category=category)

    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter == 'today':
        today = datetime.now().date()
        events = events.filter(start_time__date=today)
    elif date_filter == 'tomorrow':
        tomorrow = datetime.now().date() + timedelta(days=1)
        events = events.filter(start_time__date=tomorrow)
    elif date_filter == 'weekend':
        today = datetime.now().date()
        weekend_start = today + timedelta(days=(5-today.weekday()) % 7)
        weekend_end = weekend_start + timedelta(days=2)
        events = events.filter(start_time__date__range=[weekend_start, weekend_end])

    # Pagination logic
    paginator = Paginator(events, 6)  # Show 6 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/events_page.html', {
        'page_obj': page_obj,
        'categories': categories,
    })

# @csrf_exempt
# def save_order(request, event_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         tickets_purchased = []
#         total_amount = 0
#         orders = []


#         for ticket_item in data['tickets']:
#             ticket = Ticket.objects.get(id=ticket_item['ticket_id'])
#             quantity = ticket_item['quantity']
#             price = ticket_item['price']

#             for _ in range(quantity):
#                 # Generate a unique order ID
#                 unique_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

#                 # Create an individual order
#                 order = Order.objects.create(
#                     ticket=ticket,
#                     full_name=data['full_name'],
#                     email=data['email'],
#                     phone=data['phone'],
#                     quantity=quantity  # Save the purchased quantity
#                 )

#                 orders.append(order)

#                 # Generate barcode
#                 barcode_path = os.path.join(settings.MEDIA_ROOT, f"barcodes/order_{unique_order_id}.png")
#                 os.makedirs(os.path.dirname(barcode_path), exist_ok=True)

#                 barcode_generator = barcode.get('code128', unique_order_id, writer=ImageWriter())
#                 barcode_generator.save(barcode_path.replace('.png', ''))

#                 # Append details to the response list
#                 tickets_purchased.append({
#                     'type': ticket.type,
#                     'description': ticket.description,
#                     'unique_order_id': unique_order_id,
#                     'price': price,
#                     'barcode_url': f"{settings.MEDIA_URL}barcodes/order_{unique_order_id}.png"
#                 })

#                 total_amount += price

#         return JsonResponse({
#             'full_name': data['full_name'],
#             'email': data['email'],
#             'phone': data['phone'],
#             'tickets': tickets_purchased,
#             'total_amount': total_amount,
#             'orders': len(orders)
#         })

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

            # Generate a unique order ID for the group
            unique_order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            # Create the order for the ticket type
            order = Order.objects.create(
                ticket=ticket,
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                quantity=quantity  # Save the consolidated quantity
            )
            orders.append(order)

            # Generate barcodes for each individual ticket in the order
            for i in range(quantity):
                ticket_unique_order_id = f"{unique_order_id}-{i+1}"  # Unique barcode per ticket

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

        return JsonResponse({
            'full_name': data['full_name'],
            'email': data['email'],
            'phone': data['phone'],
            'tickets': tickets_purchased,
            'total_amount': total_amount,
            'orders': len(orders)
        })
