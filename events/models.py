from django.db import models
from django.contrib.auth.models import AbstractUser

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=ROLE_CHOICES)