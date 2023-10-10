from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProfileInfo
from .models import User
# Create your views here.


@login_required
def profile_management_site(request):
    my_profile = ProfileInfo.objects.get(user=request.user)
    context = {'user': request.user, "my_profile": my_profile}
    return render(request, "profile_management/profile_management_site.html", context)


def account_deletion(request):
    return render(request, "profile_management/account_deletion.html")


def account_management(request):
    return render(request, "profile_management/account_management.html")


def profile_showcase(request, member_id):
    try:
        my_profile = ProfileInfo.objects.get(user=member_id)
    except:
        my_profile = ProfileInfo.objects.filter(user=member_id)
    user = User.objects.get(id=member_id)
    context = {'user': user, "my_profile": my_profile}
    return render(request, "profile_management/profile_showcase.html", context)