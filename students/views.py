from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.list import ListView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, \
                                    PasswordResetConfirmView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import CourseEnrollForm, SignUpForm, ResendActivationEmailForm
from .tokens import account_activation_token
from courses.models import Course
from common.decorators import block_authenticated_user

@method_decorator(block_authenticated_user, name='get')
class SignUpView(View):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False # Deactivate account till it is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'accounts/account_activation_message.html')
        return render(request, self.template_name, {'form': form})

class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            user.profile.save()
            user.save()
            login(request, user)
            return render(request, 'accounts/account_activation_success.html')
        else:
            return render(request, 'accounts/account_activation_error.html')
            
class ResendActivationEmailLink(View):
    form_class = ResendActivationEmailForm
    template_name = 'accounts/reactivate.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            #cd = form.cleaned_data
            #email = cd['email']
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)

            current_site = get_current_site(request)
            subject = 'Activate Your Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request, 'accounts/account_activation_message.html')
        return render(request, self.template_name, {'form': form})
        
class NewPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('students:password_change_done')
    
class NewPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('students:password_reset_done')
    
class NewPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('students:password_reset_complete')

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    
    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('students:student_course_detail',
                            args=[self.course.id])

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get course object.
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # Get current module.
            context['module'] = course.modules.get(
                                    id=self.kwargs['module_id'])
        else:
            # Get first module.
            context['module'] = course.modules.all()[0]
        return context
