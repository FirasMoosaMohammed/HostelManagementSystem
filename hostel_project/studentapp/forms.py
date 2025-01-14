from django import forms
from studentapp.models import Student,Complaint,Fee


class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['phone','address']
        widgets = {
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter address'}),
        }


class FeeForm(forms.ModelForm):
    class Meta:
        model=Fee
        fields=["amount","due_date","status"]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
            'status': forms.Select(choices=Fee.options,attrs={'class': 'form-control'}),
        }

class FeePaidForm(forms.ModelForm):
    class Meta:
        model=Fee
        fields=["description"]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter payment id and mention if paid..'}),
        }
        

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject','description']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control','placeholder':'Enter description'}),
        }
