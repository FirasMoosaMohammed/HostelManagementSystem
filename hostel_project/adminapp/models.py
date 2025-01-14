from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.


class Room(models.Model):
    room_number=models.CharField(max_length=10,unique=True)
    capacity=models.PositiveIntegerField(default=1)
    occupied=models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Room {self.room_number}"
    
    @property
    def is_full(self):
        return self.occupied >= self.capacity
    
    @property
    def is_available(self):
        # A room is available if it's not fully occupied
        return self.occupied < self.capacity
    


class Booking(models.Model):
    student=models.ForeignKey('studentapp.Student', on_delete=models.CASCADE)
    room=models.ForeignKey(Room, on_delete=models.CASCADE,null=True,blank=True)
    booking_date=models.DateField(null=True,blank=True)
    checkout_date=models.DateField(null=True, blank=True)
    options=(('Pending', 'Pending'),
             ('Approved', 'Approved'),
             ('Cancelled', 'Cancelled')
    )
    status=models.CharField(max_length=20, choices=options,default='Pending')


    

    # def cancel_booking(self):
    #     if self.room:
    #         self.status = 'Cancelled'
    #         self.room.occupied -= 1  # Decrement occupied room count
    #         self.room.save()
    #         self.room = None
    #     self.save()

class Notice(models.Model):
    title=models.CharField(max_length=100)
    message=models.TextField()
    date_posted=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

    
