from django.shortcuts import render,redirect
from django.views.generic import TemplateView,ListView,CreateView
from studentapp.models import Student,Complaint,Fee
from adminapp.models import Notice,Booking
from studentapp.forms import ComplaintForm,FeePaidForm
from django.urls import reverse_lazy
from django.views import View
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
import logging
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
# Create your views here.


class StudentHomeView(LoginRequiredMixin,TemplateView):
    template_name='student_home.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        student=Student.objects.get(user=self.request.user)
        booking=Booking.objects.filter(student=student).first()
        context['student']=student
        context['booking']=booking
        return context
    

class ViewFeesView(View):

    def get(self, request, *args, **kwargs):
        student=Student.objects.get(user=self.request.user)
        fees = Fee.objects.filter(student=student)
        return render(request,"view_fees.html", {'fees': fees,'student':student, 'razorpay_key': settings.RAZORPAY_KEY_ID})

    
    
# class ViewFeesView(ListView):
#     model=Fee
#     template_name='view_fees.html'
#     context_object_name='fees'
#     pk_url_kwarg="id"

#     def get_queryset(self):
#         student=Student.objects.get(user=self.request.user)
#         return Fee.objects.filter(student=student)
    

# class PayFeesView(View):
#     def get(self,request,*args,**kwargs):
#         # amount = request.GET.get('amount')
#         fee_id=request.GET.get('id')
#         student=Student.objects.get(user=request.user)
#         fee=Fee.objects.get(id=fee_id,student=student)

#         razoramount=int(fee.amount * 100)

#         client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        

#         # print(f"Fee amount (in rupees): {fee.amount}")
#         # amount=int(fee.amount * 100)
#         # print(f"Amount (in paise): {amount}")

#         data = {
#             "amount":razoramount,
#             "currency":"INR",
#             "receipt": f"receipt_{fee.id}",
#             "payment_capture":"1",
#         }
#         payment_response=client.order.create(data=data)
#         print("Razorpay Order:", payment_response) 
        
#         order_id = payment_response['id']
#         order_status = payment_response['status']

#         if order_status == 'created':
#             payment = Fee(
#                 student=student,
#                 amount=fee.amount,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_status=order_status
#             )
#             payment.save()

#         context = {
#             'fee': fee,
#             'payment_response': payment_response,
#             'razoramount': razoramount,
#             'order_id': order_id
#         }   

#         return render(request,'view_fees.html',context)


#     def post(self, request, *args, **kwargs):
#         order_id = request.POST.get('order_id')
#         payment_id = request.POST.get('payment_id')  
#         fee_id=request.POST.get('fee_id')

#         student=Student.objects.get(user=request.user)
#         fee=Fee.objects.get(id=fee_id,student=student)
#         payment = Fee.objects.get(razorpay_order_id=order_id)

#         payment.status = 'Paid'
#         payment.razorpay_payment_id = payment_id
#         payment.save()

#         messages.success(request,"Fee Paid!")
#         return redirect('view_fees_view')

    
    # def post(self, request, *args, **kwargs):
    #     payment_id = request.POST.get('razorpay_payment_id')
    #     fee_id = request.POST.get('fee_id')
        
    #     fee = Fee.objects.get(id=fee_id)
    #     fee.status = 'Paid'
    #     fee.save()
    #     messages.success(request,"Fee Paid!")
    #     return JsonResponse({"success": True})
  

class PayFeesView(View):
    def post(self, request, *args, **kwargs):
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')
        order_id = request.POST.get('razorpay_order_id')

        fee=Fee.objects.get(razorpay_order_id=order_id)

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            # Update the payment status
            # fee = Fee.objects.get(razorpay_order_id=order_id)
            with transaction.atomic():
                fee.razorpay_payment_id = payment_id
                fee.razorpay_payment_status = 'Success'
                fee.status = 'Paid'
                fee.save()
            return redirect('payment_success')

            # return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)})
        





class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        payment_id = request.GET.get('payment_id')
        # fee_id = request.GET.get('fee_id')
        # fee=Fee.objects.get(id=fee_id)
        # fee = Fee.objects.get(razorpay_payment_id=payment_id)
        # if fee.status =='Unpaid':
        #     fee.status = "Paid"
        #     fee.save()
        return render(request, 'payment_success.html', {'payment_id': payment_id})
    
    def post(self, request, *args, **kwargs):
        # Capture the Razorpay payment details from POST
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        fee_id = request.POST.get('fee_id')

        try:
            fee = Fee.objects.get(id=fee_id)

            # Verify the payment and update fee status
            if payment_id and order_id and signature:
                fee.status = 'Paid'
                fee.razorpay_payment_id = payment_id
                fee.razorpay_payment_status = 'Success'  # Optionally save more details like payment status
                fee.save()

        except Fee.DoesNotExist:
            # Handle the case where Fee does not exist (optional)
            pass

        return redirect('view_fee_view')











 
# class PayFeesDoneView(CreateView):
#     model = Fee
#     form_class = FeePaidForm
#     template_name = 'fee_paid.html'
#     success_url=reverse_lazy('view_fees_view')

#     def form_valid(self, form):
#         fee = Fee.objects.get(id=self.kwargs['fee_id'])  # Ensure fee ID is passed in URL
#         fee.description = form.cleaned_data['description']
#         fee.save()
#         return super().form_valid(form)
# *********************************************

# class PayFeesDoneView(CreateView):
#     model = Fee
#     form_class = FeePaidForm
#     template_name = 'fee_paid.html'
#     success_url = reverse_lazy('view_fees_view')

#     def form_valid(self, form):
#         fee_id = self.request.POST.get('fee_id')
#         try:
#             fee = Fee.objects.get(id=fee_id)
#             fee.description = form.cleaned_data['description']
#             fee.save()
#         except Fee.DoesNotExist:
#             # Handle Fee not existing
#             pass
#         return super().form_valid(form)
    
class PayFeesDoneView(View):
    def get(self, request, *args, **kwargs):
        fee = Fee.objects.get(id=kwargs['fee_id'])
        form = FeePaidForm(instance=fee)
        return render(request, 'fee_paid.html', {'form': form, 'fee': fee})
    
    def post(self, request, *args, **kwargs):
        fee = Fee.objects.get(id=kwargs['fee_id'])
        form = FeePaidForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            return redirect('view_fees_view')  # Redirect to the fees list view
        return render(request, 'fee_paid.html', {'form': form, 'fee': fee})



    
class SubmitComplaintView(CreateView):
    model=Complaint
    form_class=ComplaintForm
    template_name="sub_complaint.html"
    success_url=reverse_lazy("studenthome_view")

    def form_valid(self,form):
        complaint=form.save(commit=False)
        complaint.student=Student.objects.get(user=self.request.user)
        complaint.save()
        return super().form_valid(form)
    
class StudentComplaintListView(ListView):
    model=Complaint
    template_name = 'stud_complaint.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        return Complaint.objects.filter(student__user=self.request.user)
    

class ViewNoticeView(ListView):
    model = Notice
    template_name = 'view_notices.html'
    context_object_name = 'notices'

    def get_queryset(self):
        return Notice.objects.order_by('-date_posted') 