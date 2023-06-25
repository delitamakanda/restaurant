from django.shortcuts import render
from django.http import HttpResponse

def hello_world_view(request):
    return HttpResponse(f'Hello world')
