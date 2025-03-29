from django.contrib import admin
from .models import Job, Applicant

# Register your models here.

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'type', 'location', 'created_at', 'last_date', 'filled')
    list_filter = ('type', 'filled', 'created_at')
    search_fields = ('title', 'company_name', 'location')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_description', 'website')
        }),
        ('Job Details', {
            'fields': ('location', 'type', 'category', 'last_date', 'filled')
        }),
    )


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__first_name', 'user__last_name', 'job__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Applicant Name'
