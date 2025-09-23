from django.shortcuts import render

def home(request):
    return render(request, 'base.html')

def test_styles(request):
    return render(request, 'test_styles.html')