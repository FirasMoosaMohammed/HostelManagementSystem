from django import forms
from adminapp.models import Room,Booking,Notice
from studentapp.models import Fee,Complaint
from django.contrib.auth.models import User
from django.db.models import F

class RegisterForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control","placeholder":"Enter name"}),
            "email":forms.EmailInput(attrs={"class":"form-control","placeholder":"Enter email"}),
            "password":forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}),
        }

class LoginForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","password"]
        widgets={
            "username":forms.TextInput(attrs={"class":"form-control","placeholder":"Enter name"}),
            "password":forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model=Room
        fields=['room_number','capacity']

        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter room number'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter capacity','min':1}),
        }


class StudentBookingForm(forms.ModelForm):
    class Meta:
        model=Booking
        fields = ['room','booking_date','checkout_date','status']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter room number'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control','type': 'date','placeholder': 'Select date'}),
            'checkout_date': forms.DateInput(attrs={'class': 'form-control','type': 'date','placeholder': 'Select date'}),
            'status':forms.Select(attrs={'class':'form-control','placeholder': 'Select status'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.room:
            current_room = Room.objects.filter(id=self.instance.room.id)
            self.fields['room'].queryset = Room.objects.filter(occupied__lt=F('capacity')) | current_room



class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['occupied']
        widgets = {
            'occupied': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Occupied Count'}),
        }

class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model=Complaint
        fields=['status']
        widgets = {
            'status':forms.Select(attrs={'class':'form-control'})
        }

class NoticeForm(forms.ModelForm):
    class Meta:
        model=Notice
        fields=['title','message']
        widgets = {
        "title":forms.TextInput(attrs={"class":"form-control","placeholder":"Enter title"}),
        'message': forms.Textarea(attrs={'class': 'form-control','placeholder':'Enter description'}),
        }