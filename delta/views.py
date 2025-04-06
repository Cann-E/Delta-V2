from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django import forms
from django.shortcuts import render, redirect
from .models import AcademicRequest, CustomUser
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import ChangeMajorForm, ChangeAddressForm, SignatureUploadForm
from .models import Request
from .pdf_utils import generate_pdf_for_request
from datetime import date
from .forms import RequestStatusForm





@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if user.is_active:
        user.is_active = False  # Deactivate user
        user.save()
        print(f"❌ User {user.username} has been deactivated.")

    return redirect('user_list')

def check_user_status(request):
    if request.user.is_authenticated and not request.user.is_active:
        logout(request)  # Force logout if deactivated
        return redirect('login')




class AcademicRequestForm(forms.ModelForm):
    class Meta:
        model = AcademicRequest
        fields = ['form_name', 'signature', 'document']
def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def delete_user_view(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    user.delete()
    return redirect('user_list')


@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = get_user_model().objects.all().order_by('username')
    return render(request, 'user_list.html', {'users': users})


@login_required
def home_view(request):
    template = 'home.html' if request.user.is_superuser else 'basic_dashboard.html'
    return render(request, template, {'user': request.user})


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


@login_required
def request_detail_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)
    return render(request, 'request_detail.html', {'req': req})


@login_required
def submit_request_view(request, request_id):
    req = get_object_or_404(Request, id=request_id, user=request.user)
    if req.status == 'draft':
        req.status = 'pending'
        req.save()
    return redirect('request_detail', request_id=req.id)


@login_required
def pending_requests_view(request):
    if not request.user.is_staff:
        return redirect('home')
    pending_reqs = Request.objects.filter(status='pending')
    return render(request, 'pending_requests.html', {'pending_requests': pending_reqs})


def submit_request(request):
    if request.method == "POST":
        req = Request.objects.create(
            user=request.user,
            request_type=request.POST["request_type"],
            first_name=request.user.first_name,  # ✅ Only pass these fields if they exist in the model
            last_name=request.user.last_name,
            explanation=request.POST.get("explanation", ""),
            current_major=request.POST.get("current_major", ""),
            new_major=request.POST.get("new_major", ""),
            old_address=request.POST.get("old_address", ""),
            new_address=request.POST.get("new_address", ""),
            status="pending",
        )
        return redirect("success_page")

    return render(request, "create_request.html")


@login_required
def approve_request_view(request, request_id):
    """Approve a request and generate the PDF (backend only)."""
    req = get_object_or_404(Request, id=request_id, status='pending')
    req.status = 'approved'
    req.save()

    # Generate and store PDF when approved
    pdf_path = generate_pdf_for_request(req)
    print(f"✅ PDF generated at: {pdf_path}")

    return redirect('pending_requests')


@login_required
def return_request_view(request, request_id):
    if not request.user.is_staff:
        return redirect('home')
    req = get_object_or_404(Request, id=request_id, status='pending')
    req.status = 'returned'
    req.save()
    return redirect('pending_requests')


@login_required
def user_requests_view(request):
    user_requests = Request.objects.filter(user=request.user)
    return render(request, "user_requests.html", {"requests": user_requests})


@login_required
def user_manage_requests(request):
    if not request.user.is_staff:
        return redirect('home')
    manage_requests = Request.objects.filter(status='pending')  # Fetch pending requests
    return render(request, "manage_requests.html", {"requests": manage_requests})


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


@login_required
def request_list_view(request):
    requests = Request.objects.filter(user=request.user)
    return render(request, 'request_list.html', {'requests': requests})


def success_page_view(request):
    return render(request, 'success.html')


@login_required
def upload_signature_view(request):
    if request.method == 'POST':
        form = SignatureUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SignatureUploadForm(instance=request.user)
    return render(request, 'upload_signature.html', {'form': form})


@login_required
def change_request_status(request, pk):
    req = get_object_or_404(Request, pk=pk)

    # Check if the user is allowed to change the status
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-staff users

    if request.method == 'POST' or request.method == 'GET':  # Allow both POST and GET
        new_status = request.POST.get('status') or request.GET.get('status')
        if new_status in ['approved', 'returned']:  # Validate status
            req.status = new_status
            req.save()
            if new_status == 'approved':
                # Generate and store PDF when approved
                pdf_path = generate_pdf_for_request(req)
                print(f"✅ PDF generated at: {pdf_path}")
            return redirect('pending_requests')

    return render(request, 'change_request_status.html', {'req': req})