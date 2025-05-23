from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import *

app_name = "accounts"

urlpatterns = [
    path('employee/register', RegisterEmployeeView.as_view(), name='employee-register'),
    path('employer/register', RegisterEmployerView.as_view(), name='employer-register'),
    path('employee/profile/update', EmployeeProfileUpdateView.as_view(), name='employee-profile-update'),
    path('employer/profile/update', EmployerProfileUpdateView.as_view(), name='employer-profile-update'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('login', LoginView.as_view(), name='login'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
