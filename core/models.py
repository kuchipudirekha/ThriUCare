from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class YogaVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    youtube_link = models.URLField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    phase = models.CharField(max_length=20, choices=[
        ("child", "Child"),
        ("adulthood", "Adulthood"),
        ("menopause", "Menopause"),
    ], default="adulthood")

    def __str__(self):
        return self.name or self.user.username


class GrowthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    height = models.FloatField()  # cm
    weight = models.FloatField()  # kg

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class PeriodTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    cycle_length = models.PositiveIntegerField(default=28)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_period_date(self):
        return self.start_date + timedelta(days=self.cycle_length)


class Vaccination(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("completed", "Completed"),
    ], default="pending")

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"


class Sleep(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sleep_date = models.DateField()
    hours = models.FloatField()
    quality = models.CharField(
        max_length=20,
        choices=[("Good", "Good"), ("Average", "Average"), ("Poor", "Poor")],
    )
    phase = models.CharField(
        max_length=20,
        choices=[("child", "Child"), ("adulthood", "Adulthood"), ("menopause", "Menopause")],
        default="adulthood",
    )

    def __str__(self):
        return f"{self.user.username} - {self.phase} ({self.sleep_date})"
