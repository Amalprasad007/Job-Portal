from django.urls import path, include

from jobsapp.views import *
from jobsapp.views.chat import ChatView, SendMessageView, GetMessagesView

app_name = "jobs"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),
    path('employer/dashboard/', include([
        path('', DashboardView.as_view(), name='employer-dashboard'),
        path('jobs/', EmployerJobsView.as_view(), name='employer-jobs'),
        path('jobs/<int:id>/delete/', EmployerJobDeleteView.as_view(), name='employer-jobs-delete'),
        path('jobs/edit/<int:job_id>/', EditJobView.as_view(), name='employer-jobs-edit'),
        path('all-applicants/', ApplicantsListView.as_view(), name='employer-all-applicants'),
        path('applicants/<int:job_id>/', ApplicantPerJobView.as_view(), name='employer-dashboard-applicants'),
        path('mark-filled/<int:job_id>/', filled, name='job-mark-filled'),
        path('contact-applicant/<int:applicant_id>/', ContactApplicantView.as_view(), name='contact-applicant'),
        path('view-resume/<int:applicant_id>/', ViewResumeView.as_view(), name='view-resume'),
        path('employee/<int:user_id>/', ViewEmployeeProfileView.as_view(), name='view-employee-profile'),
        path('update-application-status/<int:applicant_id>/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
    ])),
    path('chat/', include([
        path('<int:user_id>/', ChatView.as_view(), name='chat'),
        path('<int:user_id>/job/<int:job_id>/', ChatView.as_view(), name='chat-job'),
        path('send-message/', SendMessageView.as_view(), name='send-message'),
        path('get-messages/', GetMessagesView.as_view(), name='get-messages'),
    ])),
    path('employee/dashboard/', include([
        path('', AppliedJobsView.as_view(), name='employee-dashboard'),
    ])),
    path('employee/profile/', employee.EmployeeProfileView.as_view(), name='employee-profile'),
    path('employee/resume/<int:user_id>/', employee.EmployeeResumeView.as_view(), name='employee-resume'),
    path('apply-job/<int:job_id>/', ApplyJobView.as_view(), name='apply-job'),
    path('jobs/', JobListView.as_view(), name='jobs'),
    path('jobs/<int:id>/', JobDetailsView.as_view(), name='jobs-detail'),
    path('employer/jobs/create/', JobCreateView.as_view(), name='employer-jobs-create'),
]
