# core/views.py
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, date, timedelta

from .models import (
    Profile,
    GrowthRecord,
    Vaccination,
    Medication,
    PeriodTracker,
    Sleep,
    YogaVideo,
)
from .forms import (
    SignUpForm,
    GrowthForm,
    PeriodTrackerForm,
    MedicationForm,
    SleepForm,
    VaccinationForm,
    YogaForm,
)

# ------------------------------
# Home Page
# ------------------------------
def index(request):
    return render(request, 'core/index.html')


# ------------------------------
# Registration
# ------------------------------
def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            name = request.POST.get("name") or user.username
            dob = request.POST.get("dob")
            profile = Profile.objects.get(user=user)
            profile.name = name
            profile.email = user.email

            # Set user phase by age
            if dob:
                try:
                    profile.dob = datetime.strptime(dob, "%Y-%m-%d").date()
                    age = (date.today() - profile.dob).days // 365
                    if age <= 19:
                        profile.phase = "child"
                    elif 20 <= age <= 49:
                        profile.phase = "adulthood"
                    else:
                        profile.phase = "menopause"
                except Exception:
                    pass
            profile.save()
            return render(request, "core/success.html")
        else:
            return render(request, "core/register.html", {"form": form, "error": "Please correct the errors below."})
    else:
        form = SignUpForm()
    return render(request, "core/register.html", {"form": form})


# ------------------------------
# Login
# ------------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.phase == "child":
                return redirect("child")
            elif profile.phase == "adulthood":
                return redirect("adulthood")
            else:
                return redirect("menopause")
        else:
            return render(request, "core/login.html", {"error": "Invalid username or password."})
    return render(request, "core/login.html")

# ------------------------------
# Child Phase
# ------------------------------
@login_required
def child(request):
    user = request.user

    # Growth Tracking
    if request.method == 'POST' and 'growth_submit' in request.POST:
        growth_form = GrowthForm(request.POST)
        if growth_form.is_valid():
            g = growth_form.save(commit=False)
            g.user = user
            g.save()
            return redirect('child')
    else:
        growth_form = GrowthForm()

    if request.method == 'POST' and 'vaccine_submit' in request.POST:
        vac_form = VaccinationForm(request.POST)
        if vac_form.is_valid():
            v = vac_form.save(commit=False)
            v.user = user
            v.save()
            return redirect('child')
    else:
        vac_form = VaccinationForm()

    # Sleep Tracking
    if request.method == 'POST' and 'sleep_submit' in request.POST:
        sleep_form = SleepForm(request.POST)
        if sleep_form.is_valid():
            s = sleep_form.save(commit=False)
            s.user = user
            s.save()
            return redirect('child')
    else:
        sleep_form = SleepForm()

    growth_records = GrowthRecord.objects.filter(user=user)
    vaccinations = Vaccination.objects.filter(user=user)
    sleeps = Sleep.objects.filter(user=user)

    if request.method == 'POST' and 'yoga_submit' in request.POST:
        yoga_form = YogaForm(request.POST)
        if yoga_form.is_valid():
            yoga = yoga_form.save(commit=False)
            yoga.user = user
            yoga.save()
            return redirect('menopause')
    else:
        yoga_form = YogaForm()

    yoga_videos = YogaVideo.objects.filter(user=user).order_by('-id')

    context = {
        'growth_form': growth_form,
        'growth_records': growth_records,
        'vac_form': vac_form,
        'vaccinations': vaccinations,
        'sleep_form': sleep_form,
        'sleeps': sleeps,
        'yoga_form': yoga_form,
        'yoga_videos': yoga_videos,
    }
    return render(request, "core/child.html", context)


# ------------------------------
# Adulthood Phase
# ------------------------------

@login_required
def adulthood(request):
    user = request.user

    # ------------------------------
    # Handle Medication Form
    # ------------------------------
    if request.method == 'POST' and 'medication_submit' in request.POST:
        med_form = MedicationForm(request.POST)
        if med_form.is_valid():
            med = med_form.save(commit=False)
            med.user = user
            med.save()
            return redirect('adulthood')
    else:
        med_form = MedicationForm()

    # ------------------------------
    # Handle Period Tracker Form
    # ------------------------------
    if request.method == 'POST' and 'period_submit' in request.POST:
        period_form = PeriodTrackerForm(request.POST)
        if period_form.is_valid():
            p = period_form.save(commit=False)
            p.user = user
            p.save()
            return redirect('adulthood')
    else:
        period_form = PeriodTrackerForm()

    # ------------------------------
    # Handle Sleep Tracking Form
    # ------------------------------
    if request.method == 'POST' and 'sleep_submit' in request.POST:
        sleep_form = SleepForm(request.POST)
        if sleep_form.is_valid():
            s = sleep_form.save(commit=False)
            s.user = user
            s.save()
            return redirect('adulthood')
    else:
        sleep_form = SleepForm()

    # ------------------------------
    # Get user data
    # ------------------------------
    medications = Medication.objects.filter(user=user).order_by('-date_added')
    periods = PeriodTracker.objects.filter(user=user).order_by('-start_date')
    sleeps = Sleep.objects.filter(user=user)

    # ------------------------------
    # Period Reminder (2 days before)
    # ------------------------------
    today = date.today()
    # Get all period trackers where next period is in 2 days
    periods_to_remind = PeriodTracker.objects.all()
    for p in periods_to_remind:
        next_date = p.next_period_date
        if next_date - timedelta(days=2) == today:
            try:
                send_mail(
                    subject="⏰ Period Reminder - Thriucare",
                    message=f"Hi {p.user.username}, your period is expected in 2 days ({next_date}). Take care!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[p.user.email],
                    fail_silently=False,  # Set False for debugging
                )
                print(f"Reminder sent to {p.user.email} for {next_date}")
            except Exception as e:
                print(f"Failed to send email to {p.user.email}: {e}")

    if request.method == 'POST' and 'yoga_submit' in request.POST:
        yoga_form = YogaForm(request.POST)
        if yoga_form.is_valid():
            yoga = yoga_form.save(commit=False)
            yoga.user = user
            yoga.save()
            return redirect('menopause')
    else:
        yoga_form = YogaForm()

    yoga_videos = YogaVideo.objects.filter(user=user).order_by('-id')
    # ------------------------------
    # Render adulthood page
    # ------------------------------
    context = {
        'med_form': med_form,
        'medications': medications,
        'period_form': period_form,
        'periods': periods,
        'sleep_form': sleep_form,
        'sleeps': sleeps,
        'yoga_form': yoga_form,
        'yoga_videos': yoga_videos,
    }
    return render(request, "core/adulthood.html", context)

# ------------------------------
# Menopause Phase
# ------------------------------
@login_required
def menopause(request):
    user = request.user

    # --- Handle Medication Form ---
    if request.method == 'POST' and 'medication_submit' in request.POST:
        med_form = MedicationForm(request.POST)
        if med_form.is_valid():
            med = med_form.save(commit=False)
            med.user = user
            med.save()
            return redirect('menopause')
    else:
        med_form = MedicationForm()

    medications = Medication.objects.filter(user=user).order_by('-date_added')

    
    # --- Handle Sleep Form ---
    if request.method == 'POST' and 'sleep_submit' in request.POST:
        sleep_form = SleepForm(request.POST)
        if sleep_form.is_valid():
            s = sleep_form.save(commit=False)
            s.user = user
            s.save()
            return redirect('menopause')
    else:
        sleep_form = SleepForm()

    sleeps = Sleep.objects.filter(user=user).order_by('-sleep_date')

    if request.method == 'POST' and 'yoga_submit' in request.POST:
        yoga_form = YogaForm(request.POST)
        if yoga_form.is_valid():
            yoga = yoga_form.save(commit=False)
            yoga.user = user
            yoga.save()
            return redirect('menopause')
    else:
        yoga_form = YogaForm()

    yoga_videos = YogaVideo.objects.filter(user=user).order_by('-id')


    # --- Context for Template ---
    context = {
        'med_form': med_form,         
        'medications': medications,   
        'sleep_form': sleep_form,
        'sleeps': sleeps,
        'yoga_form': yoga_form,
        'yoga_videos': yoga_videos,
    }

    return render(request, "core/menopause.html", context)

    

@login_required
def logout_user(request):
    logout(request)
    return render(request, "core/logout.html")
