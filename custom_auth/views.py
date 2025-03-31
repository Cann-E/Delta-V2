from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from delta.forms import CustomUserCreationForm


def login_page(request):
    # If user is already logged in, redirect
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Get the next parameter or default to home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "custom_auth/login.html")


def logout_page(request):
    logout(request)
    return redirect('home')


def register_page(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            # Save the user and redirect to a success page
            form.save()
            messages.success(request, "Your account has been created successfully.")
            return redirect('login')  # Redirect to login page after successful registration
        else:
            messages.error(request, "There was an error with your registration.")

    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required  # This decorator ensures only logged in users can access
def home(request):
    return render(request, "home.html")