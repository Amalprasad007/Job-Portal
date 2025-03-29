from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from accounts.managers import UserManager

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female')
)

EXPERIENCE_CHOICES = (
    ('0-1', '0-1 Years'),
    ('1-3', '1-3 Years'),
    ('3-5', '3-5 Years'),
    ('5-10', '5-10 Years'),
    ('10+', '10+ Years')
)

EDUCATION_CHOICES = (
    ('high_school', 'High School'),
    ('bachelors', "Bachelor's Degree"),
    ('masters', "Master's Degree"),
    ('phd', 'Ph.D.'),
    ('other', 'Other')
)

class User(AbstractUser):
    username = None
    role = models.CharField(max_length=12, error_messages={
        'required': "Role must be provided"
    })
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False,
                            error_messages={
                                'unique': "A user with that email already exists.",
                            })
    
    # Professional Information
    headline = models.CharField(max_length=100, blank=True, null=True, 
                              help_text="Your professional headline, e.g. 'Senior Python Developer'")
    highest_education = models.CharField(
        max_length=20,
        choices=EDUCATION_CHOICES,
        blank=True,
        null=True,
        help_text="Your highest level of education"
    )
    education_details = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Details about your education (e.g., 'B.Tech in Computer Science')"
    )
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        help_text="Upload your resume (PDF, DOC, or DOCX)"
    )
    linkedin_profile = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Your LinkedIn profile URL"
    )
    github_profile = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Your GitHub profile URL"
    )
    portfolio_website = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Your portfolio website URL"
    )
    
    # Contact Information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Your contact phone number"
    )
    address = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Your current address"
    )
    
    # Professional Details
    skills = models.TextField(
        blank=True,
        null=True,
        help_text="List your key skills (comma-separated)"
    )
    experience_years = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        blank=True,
        null=True,
        help_text="Years of professional experience"
    )
    current_company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Your current company name"
    )
    current_position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Your current job position"
    )
    
    # Bio/Summary
    bio = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="A brief bio about yourself"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
