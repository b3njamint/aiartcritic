from django.shortcuts import render
from django.http import HttpResponse

# python object representing an http request
def myView(request):
    return HttpResponse("Hello, World!")
