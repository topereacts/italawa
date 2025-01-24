from django.db import models
from django.contrib.auth.models import AbstractUser
from host.models import Ticket

class User(AbstractUser):
    name = models.CharField(max_length=100)
    creator = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='events_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='events_user_set',
        blank=True
    )


class Order(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    quantity = models.PositiveIntegerField(default=1)
    unique_order_id = models.CharField(max_length=50, unique=True)  # Store unique ID for order
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.unique_order_id} for {self.full_name}"

    class Meta:
        ordering = ['-created_at']

class TicketInstance(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ticket_instances')
    ticket_unique_order_id = models.CharField(max_length=50, unique=True)
    is_checked_in = models.BooleanField(default=False)  # Tracks check-in status
    checked_in_at = models.DateTimeField(null=True, blank=True)  # Check-in timestamp