from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView, FormView, RedirectView
from accounts.forms import *
from accounts.models import User


class RegisterEmployeeView(CreateView):
    model = User
    form_class = EmployeeRegistrationForm
    template_name = 'accounts/employee/register.html'
    success_url = '/'

    extra_context = {
        'title': 'Register'
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            return redirect('accounts:login')
        else:
            return render(request, 'accounts/employee/register.html', {'form': form})


class RegisterEmployerView(CreateView):
    model = User
    form_class = EmployerRegistrationForm
    template_name = 'accounts/employer/register.html'
    success_url = '/'

    extra_context = {
        'title': 'Register'
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            return redirect('accounts:login')
        else:
            return render(request, 'accounts/employer/register.html', {'form': form})


class LoginView(FormView):
    """
        Provides the ability to login as a user with an email and password
    """
    success_url = '/'
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    extra_context = {
        'title': 'Login'
    }

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(self.request, *args, **kwargs)

    def get_success_url(self):
        if 'next' in self.request.GET and self.request.GET['next'] != '':
            return self.request.GET['next']
        else:
            # Check if user is an employer and redirect to dashboard
            if self.request.user.role == 'employer':
                return reverse('jobs:employer-dashboard')
            return self.success_url

    def get_form_class(self):
        return self.form_class

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/login'

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return super(LogoutView, self).get(request, *args, **kwargs)


class EmployeeProfileUpdateView(FormView):
    form_class = EmployeeProfileUpdateForm
    template_name = 'jobs/employee/edit-profile.html'
    success_url = '/'

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial.update({
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'gender': self.request.user.gender,
                'headline': self.request.user.headline,
                'current_position': self.request.user.current_position,
                'current_company': self.request.user.current_company,
                'experience_years': self.request.user.experience_years,
                'skills': self.request.user.skills,
                'bio': self.request.user.bio,
                'phone_number': self.request.user.phone_number,
                'address': self.request.user.address,
                'linkedin_profile': self.request.user.linkedin_profile,
                'github_profile': self.request.user.github_profile,
                'portfolio_website': self.request.user.portfolio_website,
            })
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        
        # Handle resume upload
        if 'resume' in self.request.FILES:
            user.resume = self.request.FILES['resume']
        
        user.save()
        messages.success(self.request, 'Your profile was successfully updated!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('accounts:employee-profile-update')


class EmployerProfileUpdateView(FormView):
    form_class = EmployerProfileUpdateForm
    template_name = 'jobs/employer/edit-profile.html'
    success_url = '/'

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial.update({
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'headline': self.request.user.headline,
                'bio': self.request.user.bio,
                'phone_number': self.request.user.phone_number,
                'address': self.request.user.address,
                'linkedin_profile': self.request.user.linkedin_profile,
                'portfolio_website': self.request.user.portfolio_website,
            })
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Company profile was successfully updated!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('accounts:employer-profile-update')
