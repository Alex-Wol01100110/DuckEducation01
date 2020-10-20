from django.http import Http404

def block_authenticated_user(f):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404
        f(request, *args, **kwargs)
        return f(request, *args, **kwargs)
    return wrap
