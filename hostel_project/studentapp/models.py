from django.db import models
from django.contrib.auth.models import User
from adminapp.models import Room
# Create your models here.

class Student(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    room=models.ForeignKey(Room,on_delete=models.CASCADE,null=True,blank=True)
    phone=models.BigIntegerField()
    address=models.TextField()


class Fee(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    amount=models.IntegerField()
    due_date=models.DateField()
    reg_date=models.DateTimeField(auto_now_add=True)
    options=(
        ('Paid', 'Paid'), 
        ('Unpaid', 'Unpaid')
    )
    status = models.CharField(max_length=20, choices=options,default='Unpaid')
    razorpay_order_id = models.CharField(max_length=100,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=100,blank=True,null=True,unique=True)
    razorpay_payment_status = models.CharField(max_length=100,default='Pending')
    description=models.TextField()


class Complaint(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,default=" ")
    description=models.TextField()
    date_submitted=models.DateField(auto_now_add=True)
    options=[
        ("Pending","Pending"),
        ("Resolved","Resolved"),
        ]
    status=models.CharField(max_length=20,choices=options,default='Pending')