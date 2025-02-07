from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.account.models import User, Admin, Contact

class UserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Admin)
admin.site.register(Contact)


