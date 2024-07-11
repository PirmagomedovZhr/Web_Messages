from django.shortcuts import render

def message_list(request):
    return render(request, 'message_list.html')
