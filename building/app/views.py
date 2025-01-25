from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import *
from .forms import ManagerRegistrationForm
from django.contrib.auth.forms import UserCreationForm

# manager

@permission_required('auth.add_user')
def register_building_manager(request):
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            manager = form.save(commit=False)
            manager.user.role = 'manager'
            manager.save()
            return redirect('success_page')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'register_manager.html', {'form': form})

@permission_required('app.change_buildingmanager', raise_exception=True)
def verify_manager(request, manager_id):
    """Verify a building manager."""
    manager = get_object_or_404(BuildingManager, id=manager_id)
    if request.method == 'POST':
        manager.verified = True
        manager.save()
        return HttpResponse('Manager verified successfully')
    return render(request, 'verify_manager.html', {'manager': manager})

# User Authentication

def login_user(request):
    """Login an existing user."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponse('Login successful')
        return HttpResponse('Invalid credentials', status=400)
    return render(request, 'login.html')

@login_required
def logout_user(request):
    """Logout the currently logged-in user."""
    logout(request)
    return redirect('login')

def signup_user(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('User registered successfully')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Service Management

@permission_required('app.add_service', raise_exception=True)
def define_service(request):
    """Business manager defines a new service."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        cost = request.POST.get('cost')
        available_from = request.POST.get('available_from')
        available_to = request.POST.get('available_to')
        Service.objects.create(
            name=name,
            description=description,
            cost=cost,
            available_from=available_from,
            available_to=available_to,
            business_manager=request.user
        )
        return HttpResponse('Service created successfully')
    return render(request, 'define_service.html')

@permission_required('app.can_activate_service', raise_exception=True)
def activate_service(request, service_id):
    """Activate a service."""
    service = get_object_or_404(Service, id=service_id)
    service.is_active = True
    service.save()
    return HttpResponse('Service activated successfully')

# Financial Management

@permission_required('app.add_payment', raise_exception=True)
def pay_subscription(request):
    """Pay a subscription fee."""
    if request.method == 'POST':
        subscription_id = request.POST.get('subscription_id')
        receipt_number = request.POST.get('receipt_number')
        subscription = Subscription.objects.get(id=subscription_id)
        Payment.objects.create(
            user=request.user,
            amount=subscription.amount,
            receipt_number=receipt_number
        )
        return HttpResponse('Subscription paid successfully')
    return render(request, 'pay_subscription.html')

@permission_required('app.add_billpayment', raise_exception=True)
def pay_bill(request):
    """Pay a building bill."""
    if request.method == 'POST':
        bill_id = request.POST.get('bill_id')
        amount = request.POST.get('amount')
        BillPayment.objects.create(
            building_id=request.POST.get('building_id'),
            amount=amount,
            bill_type=request.POST.get('bill_type'),
            paid_by=request.user
        )
        return HttpResponse('Bill paid successfully')
    return render(request, 'pay_bill.html')

# Issue Reporting

@login_required
def report_issue(request):
    """Resident reports an issue."""
    if request.method == 'POST':
        resident_id = request.POST.get('resident_id')
        description = request.POST.get('description')
        IssueReport.objects.create(
            resident_id=resident_id,
            description=description
        )
        return HttpResponse('Issue reported successfully')
    return render(request, 'report_issue.html')

# Wallet Management

@login_required
def charge_wallet(request):
    """Charge user's wallet."""
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        wallet = Wallet.objects.get(user=request.user)
        wallet.deposit(amount)
        return HttpResponse(f'Wallet charged successfully. New balance: {wallet.balance}')
    return render(request, 'charge_wallet.html')