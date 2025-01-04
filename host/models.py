from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone



User = settings.AUTH_USER_MODEL


class Event(models.Model):
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    undisclosed = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True)
    directions = models.TextField(blank=True)
    socials = models.URLField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    tickets_sold = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_sales(self, quantity_sold):
        self.tickets_sold += quantity_sold
        self.revenue += quantity_sold * self.price
        self.save()

class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)