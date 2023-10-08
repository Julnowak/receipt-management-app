from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def profile_management_site(request):
    context = {'user': request.user}
    return render(request, "profile_management/profile_management_site.html", context)


def account_deletion(request):
    return render(request, "profile_management/account_deletion.html")