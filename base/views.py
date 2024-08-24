from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import get_user_model

from django.contrib.auth.models import User


from .models import Medicine
from .forms import MedicineForm

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from django.utils import timezone
from datetime import timedelta

from django.core.paginator import Paginator

from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .mixins import AdminRequiredMixin
# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:  # Check if the user is an admin
                return reverse_lazy('admin:index')  # Redirect to the admin page
            return reverse_lazy('medicines')  # Redirect to the medicines page
        return super().get_success_url()  # Fallback


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('medicines')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('medicines')
        return super(RegisterPage, self).get(*args, **kwargs)



class MedicineList(LoginRequiredMixin, ListView):
    model = Medicine
    context_object_name = 'medicines'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if the user is an admin
        if self.request.user.is_staff:
            context['medicines'] = Medicine.objects.all()  # Admin sees all medicines
        else:
            context['medicines'] = context['medicines'].filter(user=self.request.user)  # Regular user sees their medicines

        # Search functionality
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['medicines'] = context['medicines'].filter(
                medicine_name__icontains=search_input)

        context['search_input'] = search_input

        # Check for expiring medicines
        one_month_from_now = timezone.now() + timedelta(days=30)
        expiring_medicines = context['medicines'].filter(expiry_date__lt=one_month_from_now)

        context['expiring_medicines'] = expiring_medicines

        # Handle pagination
        per_page = int(self.request.GET.get('per_page', 10))  # Get the number of items per page from the GET parameters, default to 10
        paginator = Paginator(context['medicines'], per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['per_page'] = per_page

        return context



class MedicineDetail(LoginRequiredMixin, DetailView):
    model = Medicine
    context_object_name = 'medicine'

class MedicineCreate(LoginRequiredMixin, CreateView):
    model = Medicine
    form_class = MedicineForm
    success_url = reverse_lazy('medicines')

    def form_valid(self, form):
        if not self.request.user.is_staff:
            # Set the user to the currently logged-in user if not admin
            form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            # Remove the 'user' field for non-admin users
            form.fields.pop('user', None)
        return form


class MedicineUpdate(LoginRequiredMixin, UpdateView):
    model = Medicine
    form_class = MedicineForm
    success_url = reverse_lazy('medicines')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            # Remove the 'user' field for non-admin users
            form.fields.pop('user', None)
        return form

class MedicineDelete(LoginRequiredMixin, DeleteView):
    model = Medicine
    context_object_name = 'medicine'
    success_url = reverse_lazy('medicines')

    def get_queryset(self):
        # Allow admins to delete any medicine, otherwise filter by the current user
        if self.request.user.is_staff:
            return self.model.objects.all()
        return self.model.objects.filter(user=self.request.user)

class UserMedicineList(LoginRequiredMixin,AdminRequiredMixin, ListView):
    model = Medicine
    context_object_name = 'medicines'
    template_name = 'base/user_medicines.html'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Medicine.objects.filter(user__id=user_id)  # Fetch medicines for the specified user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs['user_id']
        context['user'] = User.objects.get(id=user_id)  # Add the user to the context

        search_input = self.request.GET.get('search-area') or ''
        medicines = context['medicines']

        if search_input:
            medicines = medicines.filter(medicine_name__icontains=search_input)

        context['medicines'] = medicines
        context['search_input'] = search_input

        # Check for expiring medicines
        one_month_from_now = timezone.now() + timedelta(days=30)
        expiring_medicines = context['medicines'].filter(expiry_date__lt=one_month_from_now)

        context['expiring_medicines'] = expiring_medicines

         # Handle pagination
        per_page = int(self.request.GET.get('per_page', 10))  # Get the number of items per page from the GET parameters, default to 10
        paginator = Paginator(context['medicines'], per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['per_page'] = per_page

        return context

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'user_list.html'  # Replace with your template name
    context_object_name = 'users'
    
def contact_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        
        # Format the email content for admin with improved HTML
        email_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong></p>
                <p style="background-color: #f0f8ff; padding: 5px; margin: 0;">{message}</p>
            </body>
        </html>
        """
        
        # Send email to admin
        send_mail(
            f'Contact Us Form Submission from {name}',
            email_content,
            settings.DEFAULT_FROM_EMAIL,
            ['firstaidkitmgmt@gmail.com'],
            fail_silently=False,
            html_message=email_content
        )

        # Format the email content for user confirmation with improved HTML
        confirmation_email_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <p>Hi {name},</p>
                <p>Thank you for contacting us! Your message has been received, and we will get back to you shortly.</p>
                <p><strong>Here is a copy of your message:</strong></p>
                <p style="background-color: #f0f8ff; padding: 5px; margin: 0;">{message}</p>
                <p>Best regards,</p>
                <p>Admin Team</p>
            </body>
        </html>
        """

        # Send confirmation email to the user
        send_mail(
            'Confirmation of Your Contact Form Submission',
            confirmation_email_content,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=confirmation_email_content
        )
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('login')  # Redirect to the login page

    return render(request, 'contact.html')


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def test_404_view(request):
    raise Http404("This is a test 404 error.")
