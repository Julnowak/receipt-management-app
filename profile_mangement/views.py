from django.shortcuts import render

# Create your views here.


def profile_management_site(request):
    context = {'user': request.user}
    return render(request, "profile_management/profile_management_site.html")