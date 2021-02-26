from django.contrib import admin
from .models import Login, Hall, Booked, Request, Hod_Dean, Principal, Staff, Generator_Incharge

# Register your models here.
admin.site.register(Login)
admin.site.register(Hall)
admin.site.register(Booked)
admin.site.register(Request)
admin.site.register(Hod_Dean)
admin.site.register(Staff)
admin.site.register(Principal)
admin.site.register(Generator_Incharge)