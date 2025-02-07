from django.shortcuts import render


def page_not_found_view(request, exception):
    return render(request, 'error_pages/error_400.html', status=404)


def page_authentication_view(request, exception=None):
    return render(request, 'error_pages/error_401.html', status=401)


def page_forbidden_view(request, exception=None):
    return render(request, 'error_pages/error_403.html', status=403)


def page_server_error_view(request, exception=None):
    return render(request, 'error_pages/error_500.html', status=500)
