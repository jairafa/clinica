from django.contrib import admin

# Register your models here.

from api.models.profesional import *
from api.models.paciente import *
from api.models.servicio import *


admin.site.register(Paciente)
admin.site.register(Control_Ninno)
admin.site.register(Control_Joven)
admin.site.register(Control_Anciano)

admin.site.register(Profesional)

admin.site.register(Servicio)
admin.site.register(Estado_Consulta)
admin.site.register(Servicio_Consultas)