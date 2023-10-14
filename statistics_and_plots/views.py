from django.shortcuts import render

# Create your views here.


def statistics(request):
    return render(request, "statistics_and_plots/statistics.html")