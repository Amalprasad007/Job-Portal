from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from accounts.models import User

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'))


class EmployeeRegistrationForm(UserCreationForm):
    # gender = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=GENDER_CHOICES)

    def __init__(self, *args, **kwargs):
        super(EmployeeRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['gender'].required = True
        self.fields['first_name'].label = "First Name"
        self.fields['last_name'].label = "Last Name"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

        # self.fields['gender'].widget = forms.CheckboxInput()

        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter First Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Last Name',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'gender']
        error_messages = {
            'first_name': {
                'required': 'First name is required',
                'max_length': 'Name is too long'
            },
            'last_name': {
                'required': 'Last name is required',
                'max_length': 'Last Name is too long'
            },
            'gender': {
                'required': 'Gender is required'
            }
        }

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError("Gender is required")
        return gender

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "employee"
        if commit:
            user.save()
        return user


class EmployerRegistrationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(EmployerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = "Company Name"
        self.fields['last_name'].label = "Company Address"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Company Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Company Address',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        error_messages = {
            'first_name': {
                'required': 'First name is required',
                'max_length': 'Name is too long'
            },
            'last_name': {
                'required': 'Last name is required',
                'max_length': 'Last Name is too long'
            }
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.role = "employer"
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter Password'})

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user = authenticate(email=email, password=password)

            if self.user is None:
                raise forms.ValidationError("User Does Not Exist.")
            if not self.user.check_password(password):
                raise forms.ValidationError("Password Does not Match.")
            if not self.user.is_active:
                raise forms.ValidationError("User is not Active.")

        return super(UserLoginForm, self).clean(*args, **kwargs)

    def get_user(self):
        return self.user


class EmployeeProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeProfileUpdateForm, self).__init__(*args, **kwargs)
        # Basic Information
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Enter First Name',
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Enter Last Name',
        })
        
        # Professional Information
        self.fields['headline'].widget.attrs.update({
            'placeholder': 'e.g., Senior Python Developer at Tech Corp',
        })
        self.fields['current_position'].widget.attrs.update({
            'placeholder': 'e.g., Senior Developer',
        })
        self.fields['current_company'].widget.attrs.update({
            'placeholder': 'e.g., Tech Corporation',
        })
        self.fields['highest_education'].widget.attrs.update({
            'placeholder': 'Select your highest education level',
        })
        self.fields['education_details'].widget.attrs.update({
            'placeholder': 'e.g., B.Tech in Computer Science from XYZ University',
        })
        self.fields['skills'].widget.attrs.update({
            'placeholder': 'e.g., Python, Django, JavaScript, React',
        })
        self.fields['bio'].widget.attrs.update({
            'placeholder': 'Write a brief summary about your professional background and expertise',
            'rows': 4,
        })
        
        # Contact Information
        self.fields['phone_number'].widget.attrs.update({
            'placeholder': 'e.g., +1234567890',
        })
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Your current address',
            'rows': 2,
        })
        
        # Social Links
        self.fields['linkedin_profile'].widget.attrs.update({
            'placeholder': 'https://linkedin.com/in/username',
        })
        self.fields['github_profile'].widget.attrs.update({
            'placeholder': 'https://github.com/username',
        })
        self.fields['portfolio_website'].widget.attrs.update({
            'placeholder': 'https://yourportfolio.com',
        })

    class Meta:
        model = User
        fields = [
            # Basic Information
            "first_name", "last_name", "gender",
            
            # Professional Information
            "headline", "current_position", "current_company",
            "highest_education", "education_details",
            "experience_years", "skills", "bio", "resume",
            
            # Contact Information
            "phone_number", "address",
            
            # Social Links
            "linkedin_profile", "github_profile", "portfolio_website"
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'skills': forms.TextInput(),
            'highest_education': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'headline': 'Professional Headline',
            'current_position': 'Current Position',
            'current_company': 'Current Company',
            'highest_education': 'Highest Education',
            'education_details': 'Education Details',
            'experience_years': 'Years of Experience',
            'skills': 'Skills',
            'bio': 'Professional Bio',
            'resume': 'Resume',
            'phone_number': 'Phone Number',
            'address': 'Address',
            'linkedin_profile': 'LinkedIn Profile',
            'github_profile': 'GitHub Profile',
            'portfolio_website': 'Portfolio Website',
        }
        help_texts = {
            'skills': 'Separate skills with commas',
            'resume': 'Upload your resume (PDF, DOC, or DOCX)',
            'linkedin_profile': 'Your LinkedIn profile URL',
            'github_profile': 'Your GitHub profile URL',
            'portfolio_website': 'Your portfolio website URL',
        }


class EmployerProfileUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmployerProfileUpdateForm, self).__init__(*args, **kwargs)
        # Company Information
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Enter Company Name',
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Enter Company Address',
        })
        
        # Contact Information
        self.fields['phone_number'].widget.attrs.update({
            'placeholder': 'e.g., +1234567890',
        })
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Company Address',
            'rows': 2,
        })
        
        # Company Details
        self.fields['headline'].widget.attrs.update({
            'placeholder': 'e.g., Leading Tech Company in Silicon Valley',
        })
        self.fields['bio'].widget.attrs.update({
            'placeholder': 'Write a brief description about your company',
            'rows': 4,
        })
        
        # Social Links
        self.fields['linkedin_profile'].widget.attrs.update({
            'placeholder': 'https://linkedin.com/company/yourcompany',
        })
        self.fields['portfolio_website'].widget.attrs.update({
            'placeholder': 'https://yourcompany.com',
        })

    class Meta:
        model = User
        fields = [
            # Company Information
            "first_name", "last_name",
            
            # Contact Information
            "phone_number", "address",
            
            # Company Details
            "headline", "bio",
            
            # Social Links
            "linkedin_profile", "portfolio_website"
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'first_name': 'Company Name',
            'last_name': 'Company Location',
            'headline': 'Company Headline',
            'bio': 'Company Description',
            'phone_number': 'Contact Number',
            'address': 'Company Address',
            'linkedin_profile': 'Company LinkedIn',
            'portfolio_website': 'Company Website',
        }
        help_texts = {
            'headline': 'A brief tagline that describes your company',
            'bio': 'Detailed description of your company',
            'linkedin_profile': 'Your company\'s LinkedIn profile URL',
            'portfolio_website': 'Your company\'s website URL',
        }
