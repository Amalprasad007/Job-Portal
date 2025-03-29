from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse, FileResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, View, DetailView
from django.shortcuts import get_object_or_404
from django.contrib import messages
import os

from accounts.forms import EmployeeProfileUpdateForm
from accounts.models import User, GENDER_CHOICES, EDUCATION_CHOICES, EXPERIENCE_CHOICES
from jobsapp.decorators import user_is_employee
from jobsapp.forms import ApplyJobForm
from jobsapp.models import Job, Applicant

class EmployeeRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.role == 'employee':
            raise Http404
        return super().dispatch(request, *args, **kwargs)

class EditProfileView(UpdateView):
    model = User
    form_class = EmployeeProfileUpdateForm
    context_object_name = 'employee'
    template_name = 'jobs/employee/edit-profile.html'
    success_url = reverse_lazy('accounts:employer-profile-update')

    @method_decorator(login_required(login_url=reverse_lazy('accounts:login')))
    @method_decorator(user_is_employee)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            raise Http404("User doesn't exists")
        # context = self.get_context_data(object=self.object)
        return self.render_to_response(self.get_context_data())

    def get_object(self, queryset=None):
        obj = self.request.user
        print(obj)
        if obj is None:
            raise Http404("Job doesn't exists")
        return obj


class AppliedJobsView(EmployeeRequiredMixin, ListView):
    model = Applicant
    template_name = 'jobs/employee/applied-jobs.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        return Applicant.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_applications'] = self.get_queryset().count()
        context['has_shortlisted'] = self.get_queryset().filter(status='shortlisted').exists()
        return context

class ApplyJobView(LoginRequiredMixin, CreateView):
    model = Applicant
    form_class = ApplyJobForm
    template_name = 'jobs/apply-job.html'
    success_url = reverse_lazy('jobs:employee-dashboard')

    @method_decorator(user_is_employee)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = Job.objects.get(id=self.kwargs['job_id'])
        return context

    def form_valid(self, form):
        # Check if user already applied
        job = Job.objects.get(id=self.kwargs['job_id'])
        if Applicant.objects.filter(user=self.request.user, job=job).exists():
            form.add_error(None, 'You have already applied for this job')
            return self.form_invalid(form)
            
        form.instance.user = self.request.user
        form.instance.job = job
        return super().form_valid(form)

class EmployeeProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'jobs/employee/profile.html'
    context_object_name = 'employee'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        
        # Get experience years display value
        if employee.experience_years:
            context['experience_years_display'] = dict(EXPERIENCE_CHOICES).get(employee.experience_years)
        
        # Get education level display value
        if employee.highest_education:
            context['education_level_display'] = dict(EDUCATION_CHOICES).get(employee.highest_education)
        
        # Format skills as list
        if employee.skills:
            context['skills_list'] = [skill.strip() for skill in employee.skills.split(',')]
        
        # Get gender display value
        if employee.gender:
            context['gender_display'] = dict(GENDER_CHOICES).get(employee.gender)
        
        return context

class CheckResumeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_profile = get_object_or_404(User, id=request.user.id)
        has_resume = bool(user_profile.resume)  # Check if resume field is not empty
        return JsonResponse({'has_resume': has_resume})

class EmployeeResumeView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        try:
            # Get the user whose resume is being viewed
            target_user = get_object_or_404(User, id=user_id)
            
            # Check if the user has permission to view the resume
            # Allow if it's their own resume or if they're an employer
            if not (request.user.id == user_id or request.user.role == 'employer'):
                messages.error(request, "You are not authorized to view this resume.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            if not target_user.resume:
                messages.error(request, "No resume uploaded yet.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            # Get the file path and extension
            file_path = target_user.resume.path
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # For PDF files, display in browser
            if file_extension == '.pdf':
                try:
                    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                    return response
                except FileNotFoundError:
                    messages.error(request, "Resume file not found.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            # For other file types, force download
            try:
                with open(file_path, 'rb') as file:
                    response = FileResponse(file)
                    response['Content-Type'] = 'application/octet-stream'
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
            except FileNotFoundError:
                messages.error(request, "Resume file not found.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
        except Exception as e:
            messages.error(request, f"Error viewing resume: {str(e)}")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
