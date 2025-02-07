from django.urls import path
from .views import user_register, user_login, logout_func, profile

urlpatterns = [
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', logout_func, name='logout'),
    path('profile/', profile, name='profile')

]