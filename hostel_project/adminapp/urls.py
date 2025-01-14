
from django.urls import path
from adminapp import views
from django.contrib.auth import views as authview

urlpatterns = [
    path('reg',views.RegisterView.as_view(),name="reg_view"),
    path('',views.MainView.as_view(),name="main_view"),
    path('login',views.LoginView.as_view(),name="login_view"),
    path('logout',views.LogoutView.as_view(),name="logout_view"),
    path('home',views.HomeView.as_view(),name="home_view"),
    path('add/room',views.AddRoomView.as_view(),name="add_room_view"),
    path('allot/room/<int:id>',views.AllotRoomView.as_view(),name="allot_room_view"),
    path('edit/room/<int:id>',views.EditRoomView.as_view(),name="edit_room_view"),
    path('update/room/<int:id>',views.UpdateRoomView.as_view(),name="update_room_view"),
    path('delete/room/<int:id>',views.DeleteRoomView.as_view(),name="delete_room_view"),
    path('student/list',views.StudentListView.as_view(),name="student_list_view"),
    path('add/fee/<int:id>',views.AddFeeView.as_view(),name="add_fee_view"),
    path('edit/fee/<int:id>',views.EditFeeView.as_view(),name="edit_fee_view"),
    path('view/complaints',views.ComplaintListView.as_view(),name="complaint_list_view"),
    path('edit/complaints/<int:id>',views.UpdateComplaintView.as_view(),name="update_comp_view"),
    path('add/notice',views.AddNoticeView.as_view(),name="add_notice_view"),
    path('list/notices',views.NoticeListView.as_view(),name="list_notice_view"),
    path('edit/notice/<int:id>',views.UpdateNoticeView.as_view(),name="edit_notice_view"),
    path('delete/notice/<int:id>',views.DeleteNoticeView.as_view(),name="del_notice_view"),


    path('password/reset',authview.PasswordResetView.as_view(template_name="pass_reset.html"),name="password_reset"),
    path('password/reset/done',authview.PasswordResetDoneView.as_view(template_name="pass_reset_done.html"),name="password_reset_done"),
    path('password/reset/confirm/<uidb64>/<token>',authview.PasswordResetConfirmView.as_view(template_name="pass_reset_confirm.html"),name="password_reset_confirm"),
    path('password/reset/complete',authview.PasswordResetCompleteView.as_view(template_name="pass_reset_complete.html"),name="password_reset_complete"),






]
