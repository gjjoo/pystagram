from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from accounts.forms import SignupForm, UserProfileForm
from accounts.models import UserProfile


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, '회원가입 되었습니다.')

            next_url = request.GET.get('next', 'blog:index')
            return redirect(next_url)
    else:
        form = SignupForm()
    return render(request, 'form.html', {
        'form': form,
    })


@login_required
def profile_detail(request):
    profile, is_created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile_detail.html', {
        'profile': profile,
    })


@login_required
def profile_edit(request):
    profile, is_created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile 정보가 업데이트되었습니다.')
            next_url = request.GET.get('next', 'accounts.views.profile_detail')
            return redirect(next_url)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'form.html', {
        'form': form,
    })
