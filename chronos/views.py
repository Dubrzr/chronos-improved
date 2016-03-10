from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache


@never_cache
def home(request):
    return render_to_response(
        'home.html',
        context_instance=RequestContext(request)
    )