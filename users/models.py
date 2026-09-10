from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    TIER_CHOICES = (
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='free')
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    program = models.CharField(max_length=255, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    areas_of_interest = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
