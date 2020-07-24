from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from webapp.forms import RegisterForm


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard')
            else:
                print('User not found')
    else:
        form = AuthenticationForm()

    return render(request, 'user/auth/login.html', {'form': form})

def register_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/dashboard')
    else:
        form = RegisterForm()

    return render(request, 'user/auth/register.html', {'form': form})

@login_required(login_url='login')
def logout_page(request):
    logout(request)

    return redirect('/login')