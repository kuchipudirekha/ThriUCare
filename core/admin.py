# core/admin.py
from django.contrib import admin
from .models import Profile, GrowthRecord, PeriodTracker, Vaccination, Medication, Sleep

admin.site.register(Profile)
admin.site.register(GrowthRecord)
admin.site.register(PeriodTracker)
admin.site.register(Vaccination)
admin.site.register(Medication)
admin.site.register(Sleep)
