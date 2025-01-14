from django.contrib import admin
from django.urls import path
from studentapp import views
from django.contrib.auth import views as authview


urlpatterns = [
    path('student/home',views.StudentHomeView.as_view(),name="studenthome_view"),
    path('view/fees',views.ViewFeesView.as_view(),name="view_fees_view"),
    path('pay/fees/',views.PayFeesView.as_view(),name="pay_fees_view"),
    path('pay/success',views.PaymentSuccessView.as_view(),name="payment_success"),
    # path('pay/fees/done/<int:fee_id>/',views.PayFeesDoneView.as_view(),name="pay_fees_done_view"),
    path('submit/complaint',views.SubmitComplaintView.as_view(),name="sub_complaint_view"),
    path('my/complaints',views.StudentComplaintListView.as_view(),name="stud_complaint_view"),
    path('view/notices',views.ViewNoticeView.as_view(),name="view_notices_view"),


    path('password/change',authview.PasswordChangeView.as_view(template_name="pass_change.html"),name="password_change"),
    path('password/change/done',authview.PasswordChangeDoneView.as_view(template_name="pass_change_done.html"),name="password_change_done"),
    
]
