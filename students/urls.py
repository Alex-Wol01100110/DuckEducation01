from django.urls import path
from django.views.decorators.cache import cache_page
from django.contrib.auth import views as auth_views
from . import views
from common.decorators import block_authenticated_user

app_name = 'students'

urlpatterns = [
    path('enroll-course/',
         views.StudentEnrollCourseView.as_view(),
         name='student_enroll_course'),
    path('courses/',
         views.StudentCourseListView.as_view(),
         name='student_course_list'),
    path('course/<pk>/',
         cache_page(60 * 15)(views.StudentCourseDetailView.as_view()),
         name='student_course_detail'),
    path('course/<pk>/<module_id>/',
         cache_page(60 * 15)(views.StudentCourseDetailView.as_view()),
         name='student_course_detail_module'),

    path('signup/', 
         views.SignUpView.as_view(), 
         name='signup'),
    path('activate/<uidb64>/<token>/', 
         views.ActivateAccount.as_view(), 
         name='activate'),
    path('reactivate/', 
         views.ResendActivationEmailLink.as_view(), 
         name='resend_email_link'),

    path('login/', 
         block_authenticated_user(auth_views.LoginView.as_view()), 
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
         
    # Change password urls
    path('password_change/', views.NewPasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # Reset password urls
    path('password_reset/',
         views.NewPasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         views.NewPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
