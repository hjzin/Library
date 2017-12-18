from django.contrib import admin
from Bookmis.models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
class MyUserInline(admin.StackedInline):
    model = MyUser
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines=(MyUserInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Book)
admin.site.register(Borrow)
admin.site.register(LossReport)
admin.site.register(MemberLevel)
admin.site.register(BookCategory)