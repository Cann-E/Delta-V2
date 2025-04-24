from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework_simplejwt.tokens import RefreshToken
from delta.models import Request, GeneralPetition, TWResponses, RCLResponses
from delta.pdf_utils import generate_pdf_for_request, generate_general_petition_pdf, generate_tw_pdf  # Add others as needed
from django.http import FileResponse, Http404
from delta.models import Request
from django.core.files import File

from allauth.account.views import LoginView
from .pdf_utils import generate_rcl_pdf
from datetime import date
import os
import msal
import requests
import urllib.parse

# Local imports
from .models import (
    Request, GeneralPetition, Notification, CustomUser, TWResponses
)
from .forms import (
    ChangeMajorForm, ChangeAddressForm, SignatureUploadForm, RequestStatusForm,
    GeneralPetitionForm, RCLForm, TWForm
)
from .pdf_utils import generate_pdf_for_request

from delta.notifications import notify_admins, notify_user

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
        return redirect('inactive_page.html')

    if request.user.role == 'admin' or request.user.is_superuser:
        template = 'home.html'
    else:
        template = 'basic_dashboard.html'

    return render(request, template, {'user': request.user})


# create request based on request type
@login_required
def create_request_view(request, request_type):
    form_class = ChangeMajorForm if request_type == 'change_major' else ChangeAddressForm
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.first_name = request.user.first_name
            new_request.last_name = request.user.last_name
            new_request.request_type = request_type
            new_request.status = 'draft'
            new_request.save()
            return redirect('request_detail', request_id=new_request.id)
    else:
        form = form_class()

    return render(request, 'create_request.html', {'form': form, 'request_type': request_type})

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

from django.contrib import messages
import os
from django.conf import settings

@login_required
def approve_request_view(request, request_id):
    # 🔹 Try to get a standard Request (e.g., change_major, change_address)
    try:
        req = Request.objects.get(id=request_id, status='pending')
        req.status = 'approved'
        pdf_path = generate_pdf_for_request(req)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            req.pdf_file.name = relative_path
        req.save()
        notify_user(req.user, f"📄 Your {req.request_type} request PDF has been generated.")
        print(f"✅ PDF generated at: {pdf_path}")
        return redirect('pending_requests')
    except Request.DoesNotExist:
        pass

    # 🔹 Try to get a General Petition
    try:
        petition = GeneralPetition.objects.get(id=request_id)
        petition.is_finalized = True  # Optional: track approval
        pdf_path = generate_general_petition_pdf(petition)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            req.pdf_file.name = relative_path
            req.save()
        notify_user(petition.user, "📄 Your General Petition PDF has been generated.")
        print(f"✅ General Petition PDF generated at: {pdf_path}")
        return redirect('pending_requests')
    except GeneralPetition.DoesNotExist:
        pass

    # 🔹 Try to get a Term Withdrawal response
    try:
        tw = TWResponses.objects.get(id=request_id)
        pdf_path = generate_tw_pdf(tw)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            tw.pdf_file.name = relative_path
        tw.save()
        notify_user(tw.user, "📄 Your Term Withdrawal PDF has been generated.")
        print(f"✅ TW PDF generated at: {pdf_path}")
        return redirect('pending_requests')
    except TWResponses.DoesNotExist:
        pass

    # 🔹 Try to get an RCL response
    try:
        rcl = RCLResponses.objects.get(id=request_id)
        pdf_path = generate_rcl_pdf(rcl)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            rcl.pdf_file.name = relative_path
        rcl.save()
        notify_user(rcl.user, "📄 Your RCL PDF has been generated.")
        print(f"✅ RCL PDF generated at: {pdf_path}")
        return redirect('pending_requests')
    except RCLResponses.DoesNotExist:
        pass

    # 🔸 If nothing matched
    messages.error(request, "❌ Request not found or already approved.")
    return redirect('pending_requests')

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

# same create request view again (duplicate)
@login_required
def create_request_view(request, request_type):
    form_class = ChangeMajorForm if request_type == 'change_major' else ChangeAddressForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.first_name = request.POST.get("first_name", request.user.first_name)
            new_request.last_name = request.POST.get("last_name", request.user.last_name)
            new_request.request_type = request_type
            new_request.current_major = request.POST.get("current_major", "Unknown")
            new_request.status = 'draft'
            new_request.date_created = request.POST.get("date_created", date.today())
            new_request.save()
            return redirect('request_detail', request_id=new_request.id)
    else:
        form = form_class()

    return render(request, 'create_request.html', {
        'form': form,
        'request_type': request_type,
        'today_date': date.today().strftime('%Y-%m-%d')
    })

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
            form.save()
            notify_admins(f"✍️ {request.user.username} uploaded a new signature.")
            return redirect('home')
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
# ADDED: delete selected notifications
@require_POST
@login_required
def delete_notifications(request):
    ids = request.POST.getlist('notification_ids')
    Notification.objects.filter(id__in=ids, recipient=request.user).delete()
    return redirect('view_notifications')

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
def general_petition_view(request):  # FOR INTEGRATION
    if request.method == 'POST':
        form = GeneralPetitionForm(request.POST, request.FILES)
        if form.is_valid():
            petition = form.save()

        try:
            print("🖼️ Saved signature path:", petition.student_signature.path)
            print("📂 Expected folder:", os.path.dirname(petition.student_signature.path))
        except (ValueError, AttributeError):
            print("⚠️ No student signature was uploaded.")

        # ✅ Create linked request
        Request.objects.create(
            user=request.user,
            request_type='general_petition',
            first_name=petition.student_first_name,
            last_name=petition.student_last_name,
            explanation=petition.explanation,
            status='pending',
        )

        return redirect('petition_success')

    else:
        form = GeneralPetitionForm()
    return render(request, 'general_petition.html', {'form': form})



from django.shortcuts import render

def petition_success(request):
    return render(request, 'petition_success.html')  


def rcl_form_view(request):#FOR INTEGRATION
    if request.method == 'POST':
        form = RCLForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('rcl_success')
    else:
        form = RCLForm()
    return render(request, 'rcl_form.html', {'form': form})

from .pdf_utils import generate_tw_pdf

def tw_form_view(request):
    if request.method == 'POST':
        form = TWForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save()
            generate_tw_pdf(response)
            return render(request, 'tw_form.html', {'form': form, 'response': response})  # Pass response
    else:
        form = TWForm()
    return render(request, 'tw_form.html', {'form': form, 'response': None})  # Safe fallback

def submit_rcl(request):#FOR INTEGRATION
    if request.method == 'POST':
        form = RCLForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('rcl_success')
    else:
        form = RCLForm()
    return render(request, "submit_rcl.html", {"form": form})


def submit_tw(request):#FOR INTEGRATION
    if request.method == 'POST':
        form = TWForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tw_success')
    else:
        form = TWForm()
    return render(request, "submit_tw.html", {"form": form})

from .pdf_utils import generate_tw_pdf
from django.http import FileResponse

@login_required
def preview_tw_pdf(request, pk):#FOR INTEGRATION
    response = get_object_or_404(TWResponses, pk=pk)
    generate_tw_pdf(response)
    pdf_path = os.path.join(settings.MEDIA_ROOT, f"tw_{response.id}.pdf")
    return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')

from django.http import FileResponse

@login_required
def download_tw_pdf(request, response_id):
    from .models import TWResponses
    response = get_object_or_404(TWResponses, id=response_id)
    pdf_path = os.path.join(settings.MEDIA_ROOT, f"tw_{response.id}.pdf")

    if not os.path.exists(pdf_path):
        from .pdf_utils import generate_tw_pdf
        generate_tw_pdf(response)

    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"TermWithdrawal_{response.id}.pdf")

@login_required
def preview_request_pdf(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)

    if not req.pdf_file or not os.path.exists(req.pdf_file.path):
        print("\u26a0\ufe0f No existing PDF. Generating a new one...")
        pdf_path = generate_pdf_for_request(req)

        if pdf_path and os.path.exists(pdf_path):
            req.pdf_file.name = os.path.relpath(pdf_path, settings.MEDIA_ROOT).replace("\\", "/")
            req.save()
            print(f"\u2705 PDF saved to field: {req.pdf_file.name}")
        else:
            print("\u274c PDF generation failed inside preview_request_pdf")
            raise Http404("\u274c PDF generation failed.")

    return FileResponse(req.pdf_file.open('rb'), content_type='application/pdf')


@login_required
def preview_general_petition_pdf(request, request_id):
    from .models import GeneralPetition
    petition = get_object_or_404(GeneralPetition, id=request_id, user=request.user)

    if not petition.pdf_file or not os.path.exists(petition.pdf_file.path):
        raise Http404("PDF not found.")
    
    return FileResponse(petition.pdf_file.open('rb'), content_type='application/pdf')
@login_required
def preview_pdf(request, obj_type, object_id):
    if obj_type == "request":
        obj = get_object_or_404(Request, id=object_id, user=request.user)
    elif obj_type == "petition":
        obj = get_object_or_404(GeneralPetition, id=object_id, user=request.user)
    else:
        raise Http404("Invalid object type.")

    # PDF generation logic (optional for Request only)
    if not obj.pdf_file or not os.path.exists(obj.pdf_file.path):
        if obj_type == "request":
            from .pdf_utils import generate_pdf_for_request
            pdf_path = generate_pdf_for_request(obj)
            if pdf_path and os.path.exists(pdf_path):
                obj.pdf_file.name = os.path.relpath(pdf_path, settings.MEDIA_ROOT).replace("\\", "/")
                obj.save()
            else:
                raise Http404("PDF generation failed.")
        else:
            raise Http404("PDF not found.")

    return FileResponse(obj.pdf_file.open('rb'), content_type='application/pdf')



@login_required
def download_request_pdf(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)

    if not req.pdf_file or not os.path.exists(req.pdf_file.path):
        pdf_path = generate_pdf_for_request(req)
        if pdf_path:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            req.pdf_file.name = relative_path
            req.save()
        else:
            raise Http404("❌ PDF generation failed.")

    response = FileResponse(req.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="request_{req.id}.pdf"'
    return response
@login_required
def download_pdf(request, obj_type, object_id):
    if obj_type == "request":
        obj = get_object_or_404(Request, id=object_id, user=request.user)

        if not obj.pdf_file or not os.path.exists(obj.pdf_file.path):
            from .pdf_utils import generate_pdf_for_request
            pdf_path = generate_pdf_for_request(obj)
            if pdf_path:
                relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT).replace("\\", "/")
                obj.pdf_file.name = relative_path
                obj.save()
            else:
                raise Http404("❌ PDF generation failed.")
        filename = f"request_{obj.id}.pdf"

    elif obj_type == "petition":
        obj = get_object_or_404(GeneralPetition, id=object_id, user=request.user)

        if not obj.pdf_file or not os.path.exists(obj.pdf_file.path):
            raise Http404("❌ Petition PDF not found.")
        filename = f"petition_{obj.id}.pdf"

    else:
        raise Http404("Invalid object type.")

    response = FileResponse(obj.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
