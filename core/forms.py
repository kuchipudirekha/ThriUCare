from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GrowthRecord, PeriodTracker, Sleep, Medication, Vaccination,YogaVideo

class YogaForm(forms.ModelForm):
    class Meta:
        model = YogaVideo
        fields = ['title', 'youtube_link']

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class GrowthForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['height', 'weight']


class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = ['name', 'due_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class PeriodTrackerForm(forms.ModelForm):
    class Meta:
        model = PeriodTracker
        fields = ['start_date', 'cycle_length']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cycle_length': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SleepForm(forms.ModelForm):
    class Meta:
        model = Sleep
        fields = ['sleep_date', 'hours', 'quality']
        widgets = {'sleep_date': forms.DateInput(attrs={'type': 'date'})}


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
