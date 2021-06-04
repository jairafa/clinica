from django.conf.urls import url

from api.views.paciente import (
        Pacientes_APIView,
        get_Listar_Pacientes_Mayor_Riesgo_APIView,
        get_Atender_Paciente_APIView,
        get_Listar_Pacientes_Fumadores_Urgentes_APIView,

    )
from api.views.servicio import (
        get_Liberar_Consultas_APIView, 
        get_Consulta_mas_Pacientes_Atendidos_APIView,
        get_Paciente_Mas_Anciano_APIView,
    )

urlpatterns = [
    url(r'^pacientes/$',Pacientes_APIView.as_view(), name='paciente_api'), 
    url(r'^Listar_Pacientes_Mayor_Riesgo/(?P<historia>\d+)/$', get_Listar_Pacientes_Mayor_Riesgo_APIView.as_view(), name='listar_mayor_riesgo'), 
    url(r'^Atender_Paciente/$',get_Atender_Paciente_APIView.as_view(), name='atender_paciente'), 
    url(r'^Liberar_Consultas/$', get_Liberar_Consultas_APIView.as_view(), name='liberar_consultas'), 
    url(r'^Listar_Pacientes_Fumadores_Urgentes/$', get_Listar_Pacientes_Fumadores_Urgentes_APIView.as_view(), name='pacientes_fumadores'), 
    url(r'^Consulta_mas_Pacientes_Atendidos/$', get_Consulta_mas_Pacientes_Atendidos_APIView.as_view(), name='pacientes_atendidos'), 
    url(r'^Paciente_Mas_Anciano/$', get_Paciente_Mas_Anciano_APIView.as_view(), name='paciente_mas_anciano'), 

]

