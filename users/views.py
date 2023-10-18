from django.shortcuts import render,redirect
from django.contrib.auth import login
from users.forms import RegistrationForm
from profile_mangement.models import ProfileInfo
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            new_profile = ProfileInfo.objects.create(user=new_user, date_of_birth=request.POST['date_of_birth'], email=request.POST['email'])
            new_profile.save()
            login(request, new_user)
            return redirect('homepage')
    else:
        form = RegistrationForm()

    context = {'form': form }
    return render(request, 'registration/register.html', context)