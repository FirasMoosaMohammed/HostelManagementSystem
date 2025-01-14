from django.shortcuts import render,redirect
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.views.generic import TemplateView,CreateView,UpdateView,DeleteView,ListView,FormView
from adminapp.models import Room,Booking,Notice
from django.contrib.auth.models import User
from studentapp.models import Student,Fee,Complaint
from adminapp.forms import RoomForm,RegisterForm,LoginForm,StudentBookingForm,ComplaintStatusForm,NoticeForm,RoomBookingForm
from studentapp.forms import StudentForm,FeeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F
from django.db import models
from datetime import datetime
import razorpay
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

# class RegisterView(CreateView):
#     template_name='reg.html'
#     form_class=RegisterForm
#     model=User
#     # success_url=reverse_lazy('signin_view')

#     def form_valid(self,form):
#         User.objects.create_user(**form.cleaned_data)
#         messages.success(self.request,"Registration Successful!")
#         return redirect('login_view')
    
#     def form_invalid(self, form):
#         messages.warning(self.request,"User already registered!!")
#         return redirect('reg_view')

class MainView(TemplateView):
    template_name='main.html'


class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        forms = StudentForm()
        return render(request,"reg.html",{
            'form':form,
            'forms':forms,
        })
    def post(self, request, *args, **kwargs):
        form=RegisterForm(request.POST)
        forms=StudentForm(request.POST)
        if form.is_valid() and forms.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            student=forms.save(commit=False)
            student.user=user
            student.save()
            messages.success(self.request,"Registration Successful!")
            return redirect('login_view')
        return render(request,"reg.html",{
            'form':form,
            'forms':forms
        })


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form=LoginForm()
        return render(request,'login.html',{"form":form})
    
    def post(self, request, *args, **kwargs):
        usname=request.POST.get("username")
        psw=request.POST.get("password")
        user=authenticate(request,username=usname,password=psw)
        if user is not None:
            login(request,user)
            if user.is_superuser==1:
                messages.success(request,"Login Successful!")
                return redirect('home_view')
            else:
                messages.success(request,"Login Successful!")
                return redirect('studenthome_view')
            
        else:
            messages.error(request,"Invalid Credentials!")
            return redirect('login_view')

# class LoginView(View):
#     def get(self,request):
#         form=LoginForm()
#         return render(request,'login.html',{"form":form})
    
#     def post(self,request):
#         usname=request.POST.get("username")
#         psw=request.POST.get("password")
#         user=authenticate(request,username=usname,password=psw)
#         if user:
#             if user.is_superuser==1:
#                 login(request,user)
#                 messages.success(request,"Login Successful!")
#                 return redirect('home_view')
#             else:
#                 login(request,user)
#                 messages.success(request,"Login Successful!")
#                 return redirect('studenthome_view')
#         else:
#             messages.warning(request,"Invalid Credentials!")
#             return redirect('login_view')

class LogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout Successful!")
        return redirect('login_view')



class HomeView(LoginRequiredMixin,TemplateView):
    template_name="index.html"
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['rooms']=Room.objects.all()
        # context['student']=Student.objects.all()
        return context

  
class AddRoomView(CreateView):
    model=Room
    form_class=RoomForm
    template_name='add_room.html'
    success_url=reverse_lazy("home_view")

    def form_valid(self, form):
        cp=form.cleaned_data.get('capacity')
        # occ=form.cleaned_data.get('occupied')
        # if occ>cp:
        #     messages.error(self.request,"Occupancy cannot be greater than room capacity!!!")
        #     return self.form_invalid(form)
        return super().form_valid(form)
    

class UpdateRoomView(UpdateView):
    form_class=RoomForm
    template_name='update_room.html'
    model=Room
    pk_url_kwarg="id"
    success_url=reverse_lazy('home_view')

class DeleteRoomView(DeleteView):
    template_name="delete_room.html"
    model=Room
    pk_url_kwarg="id"
    success_url=reverse_lazy('home_view')

class StudentListView(ListView):
    model=Student
    template_name="student_list.html"
    context_object_name='students'

# class AddFeeView(CreateView):
#     model=Fee
#     form_class=FeeForm
#     template_name = 'add_fee.html'
#     success_url = reverse_lazy('student_list_view')
#     pk_url_kwarg="id"

#     def form_valid(self, form):
#         student=Student.objects.get(id=self.kwargs['id'])
#         form.instance.student=student
#         return super().form_valid(form)



class AddFeeView(CreateView):
    model = Fee
    form_class = FeeForm
    template_name = 'add_fee.html'
    success_url = reverse_lazy('student_list_view')
    pk_url_kwarg = "id"

    def form_valid(self, form):
        student = Student.objects.get(id=self.kwargs['id'])
        form.instance.student = student


        
        # Create a Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(form.instance.amount * 100)  # Razorpay accepts the amount in paise


        order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })
        
        # Save Razorpay order ID to Fee
        form.instance.razorpay_order_id = order['id']
        form.save()

    

        return super().form_valid(form)

    
class EditFeeView(UpdateView):
    model=Fee
    form_class=FeeForm
    template_name='edit_fee.html'
    pk_url_kwarg="id"
    success_url=reverse_lazy('student_list_view')

    def form_valid(self, form):
        if form.instance.status == "Paid":
            student=form.instance.student
            fee_amount=form.instance.amount
            to=student.user.email
            send_mail("Fee Payment Confirmation",f"Dear {student.user},\nYour fee payment of {fee_amount} have been received.Thank you!\nHostel Warden",settings.EMAIL_HOST_USER,[to])
            messages.success(self.request, f"Fee Paid by {student.user}!")
        return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.error(self.request, "Form submission failed. Please correct the errors and try again.")
        return render(self.request, 'edit_fee.html', {'form': form})
    


class AllotRoomView(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs['id']
        student = Student.objects.get(id=id)

        rooms = Room.objects.filter(occupied__lt=models.F('capacity'))
        booking_form = StudentBookingForm()
        room_form = RoomBookingForm()

        return render(request, 'allot_room.html', {
            'rooms': rooms,
            'booking_form': booking_form,
            'room_form': room_form,
            'student': student,
        })

    def post(self,request,*args,**kwargs):
        id = self.kwargs['id']
        student = Student.objects.get(id=id)

        rooms = Room.objects.filter(occupied__lt=models.F('capacity'))

        booking_form = StudentBookingForm(request.POST)
        room_form = RoomBookingForm(request.POST)

        if booking_form.is_valid() and room_form.is_valid():
            # Save the booking, but don't commit to the database yet
            booking = booking_form.save(commit=False)
            booking.student = student  # Assign the student to the booking
            booking.save()

            # Update the room's occupied count
            room = booking.room
            room.occupied = room_form.cleaned_data['occupied']
            room.save()


            messages.success(request, "Booking updated successfully.")
            return redirect('student_list_view')
        
        return render(request, 'allot_room.html', {
            'rooms': rooms,
            'booking_form': booking_form,
            'room_form': room_form,
            'student': student,
        })

# class EditRoomView(View):
#     def get(self, request, *args,**kwargs):
#         id = self.kwargs['id']
#         student = Student.objects.get(id=id)
#         latest_booking = student.booking_set.last()

#         if latest_booking:
#             booking_form = StudentBookingForm(instance=latest_booking)
#             # room_form = RoomBookingForm(instance=latest_booking.room)
#             room_form = RoomBookingForm(initial={
#                 'room': latest_booking.room.id,
#                 'occupied': latest_booking.room.occupied,
#             })
#         else:
#             booking_form = StudentBookingForm()
#             room_form = RoomBookingForm()

#         return render(request, 'allot_room.html', {
#             'student': student,
#             'booking_form': booking_form,
#             'room_form': room_form,
#         })

#     def post(self, request, *args,**kwargs):
#         id = self.kwargs['id']
#         student = Student.objects.get(id=id)
#         latest_booking = student.booking_set.last()

#         booking_form = StudentBookingForm(request.POST, instance=latest_booking)
#         room_form = RoomBookingForm(request.POST)

#         if booking_form.is_valid() and room_form.is_valid():
#             booking = booking_form.save(commit=False)
#             room = room_form.save(commit=False)

#             booking.student = student
#             booking.save()

#             room.occupied = room_form.cleaned_data['occupied']
#             room.save()

#             messages.success(request, "Room booking updated successfully.")
#             return redirect('student_list_view')

#         return render(request, 'allot_room.html', {
#             'student': student,
#             'booking_form': booking_form,
#             'room_form': room_form,
#         })


class EditRoomView(View):
    def get(self, request, *args, **kwargs):
        id = self.kwargs['id']
        student = Student.objects.get(id=id)
        latest_booking = student.booking_set.last()
        rooms = Room.objects.filter(occupied__lt=models.F('capacity'))

        if latest_booking:
            booking_form = StudentBookingForm(instance=latest_booking)
            room_form = RoomBookingForm(instance=latest_booking.room)  # Use the room instance here
        else:
            booking_form = StudentBookingForm()
            room_form = RoomBookingForm()

        return render(request, 'allot_room.html', {
            'rooms':rooms,
            'student': student,
            'booking_form': booking_form,
            'room_form': room_form,
        })

    def post(self, request, *args, **kwargs):
        id = self.kwargs['id']
        student = Student.objects.get(id=id)
        latest_booking = student.booking_set.last()
        rooms = Room.objects.filter(occupied__lt=models.F('capacity'))

        booking_form = StudentBookingForm(request.POST, instance=latest_booking)
        room_form = RoomBookingForm(request.POST, instance=latest_booking.room if latest_booking else None)

        if booking_form.is_valid() and room_form.is_valid():
            booking = booking_form.save(commit=False)
            room = room_form.save(commit=False)

            booking.student = student

            # booking.room = room
            booking.save()

            room.occupied = room_form.cleaned_data['occupied']
            room.save()

            messages.success(request, "Room booking updated successfully.")
            return redirect('student_list_view')

        return render(request, 'allot_room.html', {
            'rooms': rooms,
            'student': student,
            'booking_form': booking_form,
            'room_form': room_form,
        })












# class EditRoomView(View):
#     def get(self, request, *args, **kwargs):
#         id = self.kwargs['id']
#         student = Student.objects.get(id=id)
#         latest_booking = student.booking_set.last()

#         # Use the latest room data for form initialization
#         if latest_booking:
#             room = latest_booking.room
#             booking_form = StudentBookingForm(instance=latest_booking)
#             room_form = RoomBookingForm(initial={
#                 'room': room.id if room else None,
#                 'room_number': room.room_number if room else None,
#                 'occupied': room.occupied if room else None,
#             })
#         else:
#             booking_form = StudentBookingForm()
#             room_form = RoomBookingForm()

#         return render(request, 'allot_room.html', {
#             'student': student,
#             'booking_form': booking_form,
#             'room_form': room_form,
#         })

#     def post(self, request, *args, **kwargs):
#         id = self.kwargs['id']
#         student = Student.objects.get(id=id)
#         latest_booking = student.booking_set.last()

#         booking_form = StudentBookingForm(request.POST, instance=latest_booking)
#         room_form = RoomBookingForm(request.POST)

#         print("POST Data:", request.POST)  # Debug

#         if booking_form.is_valid() and room_form.is_valid():
#             status = booking_form.cleaned_data['status']
#             room_id = room_form.cleaned_data.get('room')
#             occupied = room_form.cleaned_data['occupied']

#             print("Form Occupied Value:", occupied)  # Debug
#             if latest_booking and latest_booking.room:
#                 print("Room Occupied Value Before Save:", latest_booking.room.occupied)  # Debug

#             if status == "Cancelled":
#                 if latest_booking:
#                     latest_booking.status = "Cancelled"
#                     latest_booking.save()
#                     if latest_booking.room:
#                         room = latest_booking.room
#                         room.occupied = max(0, occupied - 1)
#                         room.save()
#                         room.refresh_from_db()
#                         print("Room Occupied Value After Save (Cancelled):", room.occupied)  # Debug
#             else:
#                 booking = booking_form.save(commit=False)
#                 booking.student = student
#                 if room_id:
#                     room = Room.objects.get(id=room_id)
#                     booking.room = room
#                 booking.save()
#                 if room_id:
#                     room.occupied = occupied
#                     room.save()
#                     print("Room Occupied Value After Save (Approved):", room.occupied)  # Debug

#             return redirect('student_list_view')

#         print("Forms are not valid:", booking_form.errors, room_form.errors)  # Debug

#         return render(request, 'allot_room.html', {
#             'student': student,
#             'booking_form': booking_form,
#             'room_form': room_form,
#         })













    
# class AllotRoomView(FormView):
#     template_name = "allot_room.html"
#     form_class = StudentBookingForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         student_id = self.kwargs['id']
#         student = Student.objects.get(id=student_id)

#         available_rooms = Room.objects.filter(occupied__lt=F('capacity'))

#         # Get the student's latest booking, if available
#         latest_booking = student.booking_set.last()
#         room = latest_booking.room if latest_booking else None

#         # Initialize forms
#         booking_form = self.form_class(instance=latest_booking)
#         room_form = RoomBookingForm(instance=room)

#         context.update({
#             'student': student,
#             'booking_form': booking_form,
#             'room_form': room_form,
#             'rooms':available_rooms,
#         })
#         return context


#     def post(self, request, *args, **kwargs):
#         id = self.kwargs['id']
#         student = Student.objects.get(id=id)

#         # Get the latest booking and associated room
#         latest_booking = student.booking_set.last()
#         room = latest_booking.room if latest_booking else None

#         # Re-fetch the room instance to ensure up-to-date data
#         if room:
#             room.refresh_from_db()

#             print(f"Existing Room ID: {room.id}, Occupied: {room.occupied}")

#         # Bind data to forms
#         booking_form = StudentBookingForm(request.POST, instance=latest_booking)
#         room_form = RoomBookingForm(request.POST, instance=room)

#         if room_form.is_valid():
#             # print(f"Room before form save: ID={room.id}, Occupied={room.occupied}")
#             room = room_form.save(commit=False)

#             occupied = room_form.cleaned_data.get('occupied', room.occupied)
#             capacity = room.capacity

#             if capacity is not None and occupied > capacity:
#                 messages.error(request, f"Occupied value cannot exceed room capacity ({room.capacity}).")
#                 # room_form = RoomBookingForm(instance=room)
#                 return self.render_to_response(self.get_context_data(booking_form=booking_form, room_form=room_form))
            
#             room.occupied=occupied
#             room.save()

#             print(f"Room after save: ID={room.id}, Occupied={room.occupied}")
           

#         if booking_form.is_valid():
#             booking = booking_form.save(commit=False)
#             booking.student = student
#             booking.save()

#             # print(f"Form Occupied: {room_form.cleaned_data['occupied']}, Room Occupied: {room.occupied}")

#             # Validate capacity vs occupied
#             # if room.capacity is not None and room_form.cleaned_data['occupied'] > room.capacity:
#             #     messages.error(request, f"Occupied value cannot exceed room capacity ({room.capacity}).")
#             #     room_form = RoomBookingForm(instance=room)
#             #     return self.render_to_response(self.get_context_data(booking_form=booking_form, room_form=room_form))

#             # room.save()
#             # print(f"Room ID: {room.id}, Current Occupied: {room.occupied}, Form Occupied: {room_form.cleaned_data['occupied']}")

#             messages.success(request, "Booking updated successfully.")
#             return redirect(reverse_lazy('student_list_view'))
        
            
        # if not room_form.is_valid():
        #     print(f"Errors: {room_form.errors}")

        # return self.render_to_response(self.get_context_data(booking_form=booking_form, room_form=room_form))




































# class AllotRoomView(FormView):
#     template_name = "allot_room.html"
#     form_class = StudentBookingForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         id=self.kwargs['id']
#         student =Student.objects.get(id=id)
#         # latest_booking = student.booking_set.last()
#         # room = latest_booking.room if latest_booking else None
#         room_form = RoomBookingForm(instance=student.booking_set.last().room if student.booking_set.last() else None)
#         context['student'] = student
#         # context['booking_form'] = self.get_form(self.form_class)
#         context['room_form'] = room_form
#         return context

#     # def get_form(self, form_class=None):
#     #     form_class = self.get_form_class()
#     #     id=self.kwargs['id']
#     #     student =Student.objects.get(id=id)
#     #     latest_booking = student.booking_set.last()

#     #     if latest_booking:
#     #         return form_class(instance=latest_booking, **self.get_form_kwargs())
#     #     else:
#     #         return form_class(**self.get_form_kwargs())

#     def post(self, request, *args, **kwargs):
#         id=self.kwargs['id']
#         student =Student.objects.get(id=id)
#         # latest_booking = student.booking_set.last()
#         # room = latest_booking.room if latest_booking else None

#         booking_form = StudentBookingForm(request.POST, instance=student.booking_set.last())
#         room_form = RoomBookingForm(request.POST, instance=student.booking_set.last().room if student.booking_set.last() else None)

#         if booking_form.is_valid() and room_form.is_valid():
#             # Save the booking form (handles room allotment)
#             booking = booking_form.save(commit=False)
#             # if not booking.pk:  # If no existing booking, link to the student
#             booking.student = student

#             booking.save()

#             room = room_form.save(commit=False)
#             room.save()

#             # if room:
#             #     updated_room = room_form.save(commit=False)
#             #     if updated_room.occupied > updated_room.capacity:
#             #         messages.error(request, f"Occupied value cannot exceed room capacity ({updated_room.capacity}).")
#             #         return self.form_invalid(booking_form)
#             #     updated_room.save()

#             messages.success(self.request, "Booking updated successfully.")
#             return redirect(reverse_lazy('student_list_view'))
        
        
#             # Handle form errors
#         messages.error(request, "There was an error with the form submission.")
#         return self.form_invalid(booking_form)
    





























# class AllotRoomView(UpdateView):
#     model = Booking
#     form_class=StudentBookingForm
#     template_name = 'allot_room.html'
#     context_object_name = 'booking'
#     pk_url_kwarg="id"

#     def get_object(self, queryset=None):
#         # Retrieve the booking instance by primary key
#         booking_id = self.kwargs['id']
#         return Booking.objects.get(id=booking_id)

#     def form_valid(self, form):
#         booking = form.save(commit=False)
#         current_status=booking.status
#         room = booking.room
        
#         if current_status == 'Cancelled' and booking.status == 'Approved':
#             # Change from Cancelled to Approved, increment room's occupied count
#             if room and room.occupied < room.capacity:
#                 room.occupied += 1
#                 room.save()

#         elif current_status == 'Approved' and booking.status == 'Cancelled':
#             # Change from Approved to Cancelled, decrement room's occupied count
#             if room and room.occupied > 0:
#                 room.occupied -= 1
#                 room.save()
#             booking.room = None  # Unassign the room when cancelled

#         # If the room assignment changes, we ensure the room's occupied count is updated
#         booking.save()
#         return redirect(reverse_lazy('student_list_view'))
















# class AllotRoomView(FormView):
#     # model = Booking
#     form_class = StudentBookingForm
#     template_name = 'allot_room.html'
#     # success_url = reverse_lazy('student_list_view')
#     # pk_url_kwarg="id"

 
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         id = self.kwargs.get('id')
#         student =Student.objects.get(id=id)
#         context['student'] = student
#         context['rooms'] = Room.objects.filter(occupied__lt=F('capacity'))
#         return context
    
#     def get_form(self, form_class=None):
#         form_class = self.get_form_class()
#         id = self.kwargs.get('id')
#         student =Student.objects.get(id=id)
#         latest_booking = student.booking_set.last()

#         if latest_booking:
#             return form_class(instance=latest_booking, **self.get_form_kwargs())
#         else:
#             return form_class(**self.get_form_kwargs())


#     def form_valid(self, form):
#         id = self.kwargs.get('id')
#         student=Student.objects.get(id=id)
#         booking = form.save(commit=False)

#         if not booking.pk:  # If the booking doesn't exist, create one
#             booking.student = student

#         # if booking.room:
#         #     # Validate room capacity
#         #     if booking.room.is_full() and booking.status=="Approved":
#         #         messages.error(self.request, f"Room {booking.room.room_number} is full.")
#         #         return self.form_invalid(form)

#         if booking.room:    
#             if booking.status == 'Approved':
#                 # if not booking.pk or booking.status != 'Approved':  
#             # if not booking.pk or booking.status == 'Cancelled':
#                 if booking.room.occupied < booking.room.capacity:
#                     booking.room.occupied += 1
#                     booking.room.save()

#         elif booking.status == 'Cancelled':
#             # Free up the room when status changes to 'Cancelled'
#             if booking.room.occupied > 0:
#                 booking.room.occupied -= 1
#                 booking.room.save()
#             booking.room = None

#         booking.save()
#         messages.success(self.request, "Booking updated successfully.")
#         return redirect(reverse_lazy('student_list_view'))










# class AllotRoomView(CreateView):
#     model = Booking
#     form_class = StudentBookingForm
#     template_name = 'allot_room.html'
#     success_url = reverse_lazy('student_list_view')  

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         id = self.kwargs.get('id')
#         student =Student.objects.get(id=id)
#         context['student'] = student
#         context['rooms'] = Room.objects.filter(occupied__lt=F('capacity'))
#         return context
    

#     def form_valid(self, form):
#         student_id = self.kwargs.get('id')

#         student =Student.objects.get(id=student_id)
#         latest_booking = Booking.objects.filter(student=student).last()
#         new_room = form.cleaned_data['room']
#         new_status = form.cleaned_data['status']

#         # If there's an existing booking
#         if latest_booking:
#             previous_room = latest_booking.room

#             # If the new status is "Approved" update occupancy
#             if new_status == "Approved":
#                 # Decrease occupancy for the previous room if applicable
#                 if previous_room and previous_room != new_room:
#                     previous_room.occupied -= 1
#                     previous_room.save()

#                 # Increase occupancy for the new room
#                 new_room.occupied += 1
#                 new_room.save()

#                 # Update the latest booking
#                 latest_booking.room = new_room
#                 latest_booking.booking_date = form.cleaned_data['booking_date']
#                 latest_booking.checkout_date = form.cleaned_data['checkout_date']
#                 latest_booking.status = new_status
#                 latest_booking.save()

#             elif new_status == "Cancelled":
#                 # Decrease occupancy for the room if applicable
#                 if previous_room:
#                     previous_room.occupied -= 1
#                     previous_room.save()

#                 # Update the status to "Cancelled"
#                 latest_booking.status = new_status
#                 latest_booking.save()

#         else:
#             # If no existing booking, create a new one
#             form.instance.student = student
#             form.save()

#             # Increase occupancy for the assigned room
#             new_room.occupied += 1
#             new_room.save()

#         return super().form_valid(form)


        # existing_booking = Booking.objects.filter(student=student).first()
        
        # if form.cleaned_data['status'] == 'Approved':
        #     if existing_booking:
        #         previous_room = existing_booking.room
        #         if previous_room:  # Decrease occupancy of the old room if it exists
        #             previous_room.occupied -= 1
        #             previous_room.save()

        #         existing_booking.room = form.cleaned_data['room']
        #         existing_booking.status = 'Approved'
        #         existing_booking.student = student
        #         print(f"Updating booking: {existing_booking}, student: {existing_booking.student}") 
        #         existing_booking.save()
                
        #         new_room = form.cleaned_data['room']
        #         new_room.occupied += 1
        #         new_room.save()
        #     else:
        #         booking = form.save(commit=False)  # Don't save yet
        #         # print(f"Booking before saving: {booking}, Student: {booking.student}")
        #         booking.student = student
        #         print(f"Before saving new booking: {booking}, Student: {booking.student}")
        #         booking.save()
        #         # print(f"Booking saved successfully: {booking}")
               
                    
        #         room = form.cleaned_data['room']
        #         room.occupied += 1
        #         room.save()

        
        # elif form.cleaned_data['status'] == 'Cancelled':
        #     if existing_booking:
        #         previous_room = existing_booking.room
        #         if previous_room:  # Decrease occupancy of the room if it exists
        #             previous_room.occupied -= 1
        #             previous_room.save()
                
        #         existing_booking.status = 'Cancelled'
        #         existing_booking.student = student
        #         print(f"Cancelling booking: {existing_booking}, student: {existing_booking.student}")  
        #         existing_booking.save()
        #     else:
        #         # pass
        #         print("No existing booking found to cancel.")

        # print("Form valid; proceeding to save.")
        # return super().form_valid(form)




    

class ComplaintListView(ListView):
    model=Complaint
    template_name = 'view_complaint.html'
    context_object_name = 'complaints'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
        

class UpdateComplaintView(UpdateView):
    model=Complaint
    form_class=ComplaintStatusForm
    template_name="edit_comp.html"
    success_url=reverse_lazy("complaint_list_view")
    pk_url_kwarg="id"


class AddNoticeView(CreateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'add_notice.html'
    success_url=reverse_lazy('list_notice_view')

class NoticeListView(ListView):
    model = Notice
    template_name = 'list_notices.html'
    context_object_name = 'notices'

    def get_queryset(self):
        return Notice.objects.order_by('-date_posted') 
    
class UpdateNoticeView(UpdateView):
    form_class=NoticeForm
    template_name='update_notice.html'
    model=Notice
    pk_url_kwarg="id"
    success_url=reverse_lazy('list_notice_view')

class DeleteNoticeView(DeleteView):
    template_name="delete_notice.html"
    model=Notice
    pk_url_kwarg="id"
    success_url=reverse_lazy('list_notice_view')