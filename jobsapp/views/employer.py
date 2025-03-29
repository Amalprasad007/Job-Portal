from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, View, DetailView, DeleteView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, FileResponse, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os
from wsgiref.util import FileWrapper

from jobsapp.decorators import user_is_employer
from jobsapp.forms import CreateJobForm
from jobsapp.models import Job, Applicant
from accounts.models import GENDER_CHOICES, EDUCATION_CHOICES, EXPERIENCE_CHOICES

User = get_user_model()

class EmployerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'employer'

class DashboardView(LoginRequiredMixin, EmployerRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/employer/dashboard.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_jobs = self.get_queryset()
        context['total_jobs'] = user_jobs.count()
        context['total_filled'] = user_jobs.filter(filled=True).count()
        context['total_applicants'] = Applicant.objects.filter(job__user=self.request.user).count()
        return context

class ApplicantPerJobView(LoginRequiredMixin, EmployerRequiredMixin, ListView):
    model = Applicant
    template_name = 'jobs/employer/applicants.html'
    context_object_name = 'applicants'
    paginate_by = 5

    def get_queryset(self):
        return Applicant.objects.filter(job_id=self.kwargs['job_id']).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = Job.objects.get(id=self.kwargs['job_id'])
        return context

class JobCreateView(LoginRequiredMixin, EmployerRequiredMixin, CreateView):
    template_name = 'jobs/create.html'
    form_class = CreateJobForm
    extra_context = {
        'title': 'Post New Job'
    }
    success_url = reverse_lazy('jobs:employer-dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(JobCreateView, self).form_valid(form)

class ApplicantsListView(LoginRequiredMixin, EmployerRequiredMixin, ListView):
    model = Applicant
    template_name = 'jobs/employer/all-applicants.html'
    context_object_name = 'applicants'

    def get_queryset(self):
        queryset = self.model.objects.filter(job__user_id=self.request.user.id)
        
        # Get filter parameters
        sort_by = self.request.GET.get('sort')
        job_filter = self.request.GET.get('job')
        status_filter = self.request.GET.get('status')

        # Apply sorting
        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')

        # Filter by job
        if job_filter:
            queryset = queryset.filter(job_id=job_filter)

        # Filter by status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add jobs for filtering
        context['jobs'] = Job.objects.filter(user_id=self.request.user.id)
        # Add current filters
        context['current_sort'] = self.request.GET.get('sort', '')
        context['current_job'] = self.request.GET.get('job', '')
        context['current_status'] = self.request.GET.get('status', '')
        return context

class ContactApplicantView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def post(self, request, applicant_id):
        applicant = Applicant.objects.get(id=applicant_id)
        
        # Verify that this applicant applied to a job posted by the current employer
        if applicant.job.user != request.user:
            messages.error(request, "You are not authorized to contact this applicant.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            # Send email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [applicant.user.email],
                fail_silently=False,
            )
            messages.success(request, "Message sent successfully!")
        except Exception as e:
            messages.error(request, f"Failed to send message: {str(e)}")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class ViewResumeView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def get(self, request, applicant_id):
        try:
            applicant = Applicant.objects.get(id=applicant_id)
            
            # Verify that this applicant applied to a job posted by the current employer
            if applicant.job.user != request.user:
                messages.error(request, "You are not authorized to view this resume.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            if not applicant.user.resume:
                messages.error(request, "No resume uploaded by this applicant.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            # Get the file path and extension
            file_path = applicant.user.resume.path
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # For PDF files, display in browser
            if file_extension == '.pdf':
                try:
                    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                    return response
                except FileNotFoundError:
                    raise Http404()
            
            # For other file types (doc, docx), force download
            else:
                try:
                    wrapper = FileWrapper(open(file_path, 'rb'))
                    content_type = 'application/msword'
                    if file_extension == '.docx':
                        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    
                    response = HttpResponse(wrapper, content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    return response
                except FileNotFoundError:
                    raise Http404()
            
        except Applicant.DoesNotExist:
            messages.error(request, "Applicant not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class UpdateApplicationStatusView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def post(self, request, applicant_id):
        try:
            applicant = get_object_or_404(Applicant, id=applicant_id, job__user=request.user)
            status = request.POST.get('status')
            
            if status not in ['waiting', 'shortlisted', 'rejected']:
                return JsonResponse({'error': 'Invalid status'}, status=400)
                
            applicant.status = status
            applicant.save()
            
            return JsonResponse({
                'success': True,
                'status': status,
                'message': f'Application status updated to {status}'
            })
            
        except Applicant.DoesNotExist:
            return JsonResponse({'error': 'Applicant not found'}, status=404)

class EmployerJobsView(LoginRequiredMixin, EmployerRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/employer/employer_jobs.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return self.model.objects.filter(user_id=self.request.user.id).order_by('-created_at')

class EditJobView(LoginRequiredMixin, EmployerRequiredMixin, View):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, user=request.user)
        
        # Update job fields
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.type = request.POST.get('type')
        job.category = request.POST.get('category')
        job.company_name = request.POST.get('company_name')
        job.company_description = request.POST.get('company_description')
        job.website = request.POST.get('website')
        job.location = request.POST.get('location')
        job.last_date = request.POST.get('last_date')
        job.save()
        
        messages.success(request, 'Job updated successfully!')
        return HttpResponseRedirect(reverse_lazy('jobs:employer-jobs'))

class EmployerJobDeleteView(LoginRequiredMixin, EmployerRequiredMixin, DeleteView):
    model = Job
    pk_url_kwarg = 'id'
    template_name = 'jobs/employer/employer_jobs.html'
    success_url = reverse_lazy('jobs:employer-jobs')

    def get(self, request, *args, **kwargs):
        return redirect('jobs:employer-jobs')

    def post(self, request, *args, **kwargs):
        job = self.get_object()
        if job.user != self.request.user:
            messages.error(request, "You cannot delete this job posting.")
            return redirect('jobs:employer-jobs')
        messages.success(request, f"Job posting '{job.title}' has been deleted successfully.")
        return super().post(request, *args, **kwargs)

class ViewEmployeeProfileView(LoginRequiredMixin, EmployerRequiredMixin, DetailView):
    model = User
    template_name = 'jobs/employer/view_employee_profile.html'
    context_object_name = 'employee'
    pk_url_kwarg = 'user_id'

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
            
        # Get job applications
        context['applications'] = Applicant.objects.filter(user=employee)
        
        return context

@login_required(login_url=reverse_lazy('accounts:login'))
@user_is_employer
def filled(request, job_id):
    job = get_object_or_404(Job, user_id=request.user.id, id=job_id)
    job.filled = not job.filled  # Toggle the filled status
    job.save()
    messages.success(request, f"Job marked as {'filled' if job.filled else 'active'}")
    return HttpResponseRedirect(reverse_lazy('jobs:employer-dashboard'))
