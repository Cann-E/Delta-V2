import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, authenticate, logout
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.http import require_POST
from django.contrib.auth.backends import ModelBackend

from allauth.account.views import LoginView

from .forms import ChangeMajorForm, ChangeAddressForm, SignatureUploadForm
from .models import Request
from .pdf_utils import generate_pdf_for_request
from datetime import date
from .forms import RequestStatusForm
from delta.models import CustomUser
from .models import Notification
from delta.notifications import notify_admins, notify_user

import msal
import requests
import urllib.parse
import re


# check if user is admin
def is_admin(user):
    return user.is_staff or user.is_superuser

# admin can delete user
@login_required
@user_passes_test(is_admin)
def delete_user_view(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    user.delete()
    notify_admins(f"❌ {user.username} was deleted by {request.user.username}")
    return redirect('user_list')

# admin can see list of users
@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = get_user_model().objects.all().order_by('username')
    return render(request, 'user_list.html', {'users': users})

# loads dashboard depending on user type
@login_required
def home_view(request):
    print("Home view hit. is_active =", request.user.is_active)
    if not request.user.is_active:
        return redirect('inactive_page.html')# Prevents the redirect loop
    if request.user.role == 'admin':
        template = 'home.html'
    else:
        template = 'basic_dashboard.html'

    return render(request, template, {'user': request.user})

def latex_escape(s):
    """Escape LaTeX special characters in a string."""
    if not s:
        return ""
    return re.sub(r'([#\$%&~_^\\{}])', r'\\\1', str(s))
# create request based on request type
@login_required
def create_request_view(request, request_type):
    # Choose the appropriate form class based on the request type
    if request_type == 'change_major':
        form_class = ChangeMajorForm
    elif request_type == 'change_address':
        form_class = ChangeAddressForm
    else:
        # Default or handle error
        form_class = ChangeMajorForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.request_type = request_type  # set the request type
            new_request.save()

            # Choose the right LaTeX template based on request_type
            if request_type == 'change_major':
                template_name = 'change_major.tex'
            elif request_type == 'change_address':
                template_name = 'change_address.tex'
            else:
                template_name = 'default_request.tex'

            # Build the full path to the template file
            template_path = os.path.join(settings.BASE_DIR, 'delta', 'PDF', template_name)

            # Prepare context for LaTeX rendering
            context = {
                'user': request.user, 
                'first_name': latex_escape(request.user.first_name),
                'last_name': latex_escape(request.user.last_name),
                'request_type': latex_escape(new_request.request_type),
                'explanation': latex_escape(new_request.explanation),
                'current_major': latex_escape(new_request.current_major),
                'new_major': latex_escape(new_request.new_major),
                'old_address': latex_escape(new_request.old_address),
                'new_address': latex_escape(new_request.new_address),
            }

            # Set the output file name
            output_filename = f"request_{new_request.pk}.pdf"

            # Generate the PDF
            path = generate_pdf_for_request(template_path, context, output_filename)

            if path:
                # Save the relative path so Django can serve the file via MEDIA_URL
                new_request.pdf_file.name = os.path.relpath(path, settings.MEDIA_ROOT)
                new_request.save(update_fields=["pdf_file"])
                print(f"[SUCCESS] PDF generated and attached: {path}")
            else:
                print("[ERROR] Failed to generate PDF")

            return redirect('request_detail', request_id=new_request.id)
    else:
        form = form_class()

    return render(request, 'create_request.html', {'form': form})

# shows request details
@login_required
def request_detail_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)
    return render(request, 'request_detail.html', {'req': req})

# change request status from draft to pending
@login_required
def submit_request_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)
    if req.status == 'draft':
        req.status = 'pending'
        req.save()
    notify_admins(f"📄 {request.user.username} submitted a {req.request_type} request.")
    return redirect('request_detail', request_id=req.id)

# admin can view all pending requests
@login_required
def pending_requests_view(request):
    if not request.user.is_staff:
        return redirect('home')
    pending_reqs = Request.objects.filter(status='pending')
 
    for req in pending_reqs:
        # Skip if we already have a PDF on file
        if req.pdf_file:
            continue
        
        pdf_path = generate_pdf_for_request(req)
        if pdf_path and os.path.exists(pdf_path):
            # Open the local file in binary mode and attach to the model
            with open(pdf_path, 'rb') as f:
                req.pdf_file.save(f"request_{req.id}.pdf", File(f), save=True)
    
    return render(request, 'pending_requests.html', {'pending_requests': pending_reqs})

# submit request using POST
def submit_request(request):
    if request.method == "POST":
        req = Request.objects.create(
            user=request.user,
            request_type=request.POST["request_type"],
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            explanation=request.POST.get("explanation", ""),
            current_major=request.POST.get("current_major", ""),
            new_major=request.POST.get("new_major", ""),
            old_address=request.POST.get("old_address", ""),
            new_address=request.POST.get("new_address", ""),
            status="pending",
        )
        
        notify_admins(
            f"📥 New request submitted by {request.user.username} — type: {req.request_type}"
        )
        
        return redirect("success_page")
    return render(request, "create_request.html")

# approve pending request and make PDF
@login_required
def approve_request_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, status='pending')

    # Mark it approved
    req.status = 'approved'
    req.save()

    # Update user data if it’s a major or address request
    if req.request_type == 'change_major':
        req.user.major = req.new_major
        req.user.save()
    elif req.request_type == 'change_address':
        req.user.address = req.new_address
        req.user.save()

    # Generate PDF
    pdf_path = generate_pdf_for_request(req)

    # Save PDF path to the request object (if your model has a FileField)
    if pdf_path:
        relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
        req.pdf_file.name = relative_path  # assumes FileField named 'pdf_file'
        req.save()

        notify_user(req.user, f"📄 Your {req.request_type} request PDF has been generated.")
        print(f"✅ PDF generated at: {pdf_path}")

    return redirect('pending_requests')

# return request to user (change status)
@login_required
def return_request_view(request, request_id):
    if not request.user.is_staff:
        return redirect('home')
    req = get_object_or_404(Request, id=request_id, status='pending')
    req.status = 'returned'
    req.save()
    notify_user(req.user, f"🔁 Your {req.request_type} request was returned by {request.user.username}.")
    return redirect('pending_requests')

# user can view their own requests
@login_required
def user_requests_view(request):
    user_requests = Request.objects.filter(user=request.user)
    return render(request, "user_requests.html", {"requests": user_requests})

# show list of requests for user
@login_required
def request_list_view(request):
    requests = Request.objects.filter(user=request.user)
    return render(request, 'request_list.html', {'requests': requests})

# shows success message
def success_page_view(request):
    return render(request, 'success.html')

# upload user signature
@login_required
def upload_signature_view(request):
    if request.method == 'POST':
        form = SignatureUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            uploaded_file = request.FILES.get('signature')

            if uploaded_file:
                filename = f"user_{request.user.id}_signature.png"
                signature_dir = os.path.join(settings.MEDIA_ROOT, 'signatures')
                os.makedirs(signature_dir, exist_ok=True)

                signature_path = os.path.join(signature_dir, filename)

                # ✅ save the uploaded file manually with predictable name
                with open(signature_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # ✅ assign the path to the user's model
                request.user.signature.name = f"signatures/{filename}"
                request.user.save()

            return redirect('home')  # or wherever you'd like to redirect after upload
    else:
        form = SignatureUploadForm(instance=request.user)

    return render(request, 'upload_signature.html', {'form': form})


# admin can change request status
@login_required
def change_request_status(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if not request.user.can_change_request_status(req):
        return redirect('some_error_view')
    if request.method == 'POST':
        form = RequestStatusForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            return redirect('some_success_view')
    else:
        form = RequestStatusForm(instance=req)
    return render(request, 'change_request_status.html', {'form': form})

# admin can activate/deactivate user
@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_superuser:
        user.is_active = not user.is_active
        user.save()
    return redirect('user_list')

# redirect inactive users to a different page
@login_required
def inactive_page(request):
    return render(request, 'inactive_page.html')  # stay here otherwise

# page to show if user is inactive
def inactive(request):
    return render(request, 'inactive')

def get_msal_app():
    return msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH_CLIENT_ID,
        authority=settings.MICROSOFT_AUTHORITY,
        client_credential=settings.MICROSOFT_AUTH_CLIENT_SECRET,
    )

def microsoft_login(request):
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_AUTH_REDIRECT_URI,
        prompt='login'  # Forces re-authentication
    )
    return redirect(auth_url)

def microsoft_callback(request):
    print(">>> Received Microsoft callback")
    if "code" not in request.GET:
        print(">>> No code in request.GET")
        messages.error(request, "Microsoft login failed. Please try again.")
        return redirect("/accounts/login/")

    msal_app = get_msal_app()
    token_response = msal_app.acquire_token_by_authorization_code(
        request.GET["code"],
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_AUTH_REDIRECT_URI,
    )
    print(">>> Token response:", token_response)
    if "access_token" not in token_response:
        error_msg = token_response.get("error_description", "Unknown error")
        print(">>> Error acquiring token:", error_msg)
        messages.error(request, f"Microsoft login failed: {error_msg}")
        return redirect("/accounts/login/")

    user_info = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token_response['access_token']}"},
    ).json()

    email = (user_info.get("mail") or user_info.get("userPrincipalName") or "").lower()
    name = user_info.get("displayName", "Unknown User")

    if not email:
        messages.error(request, "Could not retrieve email from Microsoft.")
        return redirect("/accounts/login/")
    
    auto_activate = email.endswith('.edu')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(
            email=email,
            username=email.split('@')[0],
            first_name=name,
            is_active=email.endswith('.edu')  # ✅ auto-activate if .edu
        )
        user.set_password(CustomUser.objects.make_random_password())
        user.save()
    if not user.is_active:
        notify_admins(f"🆕 New user registered: {user.email} ({user.username}) — account pending activation.")
    if user.is_active:
        notify_admins(f"✅ {user.username} ({user.email}) just logged in.")

    user.backend = "django.contrib.auth.backends.ModelBackend"
    print(">>> Logging in user:", user.email)
    login(request, user)
    request.session["is_microsoft_login"] = True # Track it's a Microsoft login

    print(">>> Login succeeded, saving session.")
    request.session.save()
    user = get_user_model().objects.get(id=user.id)
    print(">>> User authenticated?", request.user.is_authenticated)
    print(">>> User active?", request.user.is_active)

    refresh = RefreshToken.for_user(user)
    request.session["access_token"] = str(refresh.access_token)
    request.session["refresh_token"] = str(refresh)
    #testing print
    print(">>> User info:", user_info)
    print(">>> User authenticated?", request.user.is_authenticated)

    if not user.is_active:
        print(">>> User is inactive, redirecting to inactive_page")
        return redirect("inactive_page")

    messages.success(request, f"Welcome back, {user.first_name}!")
    return redirect("/")

#FIXED: error when local account logs out, instead of sending back to account/login/, they get 
#       sent to Microsoft authentication log in procedure, then the Microsoft account is 
#       logged in. Loop of not being able to log out, basically
def microsoft_logout(request):
    # STEP 1: Store value in local variable first
    is_microsoft_login = request.session.get("is_microsoft_login", False)

    # STEP 2: Do logout and flush (losing the token status of logging out Microsoft, hence we store it in local var)
    logout(request)
    request.session.flush()

    # STEP 3: Use the stored value safely
    if is_microsoft_login:
        microsoft_logout_url = "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        post_logout_redirect_uri = request.build_absolute_uri("/accounts/login/")
        logout_redirect_url = (
            f"{microsoft_logout_url}?post_logout_redirect_uri={urllib.parse.quote(post_logout_redirect_uri)}"
        )
        return redirect(logout_redirect_url)

    return redirect("/accounts/login/")

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["is_microsoft_login"] = False  # It's a local login
        return response

#NAM2
@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


#NAM2
@login_required
@require_POST
def toggle_read_status(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = not notif.is_read
    notif.save()
    return redirect('view_notifications')

@login_required
def unread_count_view(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def pdf_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)
    if req.pdf_file:
        pdf_path = req.pdf_file.url
        return redirect(pdf_path)
    else:
        messages.error(request, "PDF not found.")
        return redirect('request_detail', request_id=req.id)