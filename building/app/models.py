# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Base User model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('manager', 'Building Manager'),
        ('business', 'Business Owner'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='resident')

    # for django config
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

# Resident Profile
class Resident(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('tenant', 'Tenant'),
        ('visitor', 'Visitor'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'resident'})
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    resident_type = models.CharField(max_length=50, choices=ROLE_CHOICES)


# Manager Profile
class BuildingManager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'manager'})
    building = models.OneToOneField(Building, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    approved_by_admin = models.BooleanField(default=False)

class ManagementTransferRequest(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    new_manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'manager'})
    approved = models.BooleanField(default=False)

# Business Profile
class BusinessOwner(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'business'})
    business_name = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)

# service
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    building_manager = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'manager'},
        related_name='services_by_building_manager'  
    )
    business_manager = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'business'},
        related_name='services_by_business_manager'  
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_activate_service", "Can activate service"),
        ]

# service request
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  
    requested_at = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    additional_info = models.TextField(null=True, blank=True) 

# Financial management

class Subscription(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()



class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=100, unique=True)
    modified_at = models.DateTimeField(auto_now=True)

class BillPayment(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    payment_ino = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name= 'bill_payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_type = models.CharField(max_length=50, choices=[('electricity', 'Electricity'), ('water', 'Water'), ('gas', 'Gas')])
    paid_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_locked = models.BooleanField(default=False)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

# connections
class Announcement(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=50, choices=[('all', 'All Users'), ('residents', 'Residents'), ('managers', 'Managers'), ('businesses', 'Businesses')], default='all')

    class Meta:
        permissions = [
            ("can_create_announcement", "Can create announcement"),
        ]

class Reminder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    send_at = models.DateTimeField()
    sent = models.BooleanField(default=False)

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=[('sent', 'Sent'), ('failed', 'Failed')], default='sent', max_length=10)


# survey and response
class Survey(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    response = models.TextField()


# issue
class IssueReport(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    updated_at = models.DateTimeField(auto_now=True)  # تاریخ آخرین به‌روزرسانی
    notes = models.TextField(null=True, blank=True)  # توضیحات اضافی

# FAQ
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# contract
class Contract(models.Model):
    manager = models.ForeignKey(BuildingManager, on_delete=models.CASCADE)
    details = models.TextField()
    verified = models.BooleanField(default=False)
    status = models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

