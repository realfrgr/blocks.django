from django import forms
from .models import Post , Tournament
from django.contrib.auth.models import User



class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=["title",'content']
      


class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ["name", "max_participants"]
        widgets = {
            'max_participants': forms.NumberInput(attrs={'min': 2, 'step': 2}),
        }