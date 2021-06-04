from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q

from api.models.paciente import *
from api.models.servicio import *
from api.serializers.paciente import *
#from api.users.authentication_mixins import Authentication

#class get_Listar_Pacientes_Mayor_Riesgo_APIView(Authentication, APIView):
class get_Listar_Pacientes_Mayor_Riesgo_APIView(APIView):
	"""
	Dado un número de historia clínica, listar todos los pacientes con mayor riesgo 
	que el del paciente al que pertenece el número de historia clínica dado.
	"""

	def get(self, request, historia):
		#print(f"user {self.user}")
		#print(f"user {request.user}")
		#print(f"username {self.user.username}")
		#print(f"historia {historia}")

		try:
			listaPacientes = []
			paciente = Paciente.objects.get(historia = historia)
			#print(f"Solicitado {paciente}")
			pacientes = Paciente.objects.all()
			for p in pacientes:
				#print(f"Buscado {p}")
				if p.get_riesgo() > paciente.get_riesgo():
					listaPacientes.append(p)

			if len(listaPacientes)>0:
				serializer_class = PacienteSerializer (listaPacientes, many = True)
				return Response(serializer_class.data, status.HTTP_200_OK)

			return Response({
			'error': 'No encontrados pacientes con riezgo mayor para la historia (' + historia + ') '
			},status = status.HTTP_404_NOT_FOUND)

		except:
			return Response({
				'error': 'Historia (' + historia + ') no encontrada'
			},status = status.HTTP_404_NOT_FOUND)


class get_Listar_Pacientes_Fumadores_Urgentes_APIView(APIView):
	"""
	Lista el nombre de los pacientes fumadores que necesitan ser atendidos con urgencia.  
	"""

	def get(self, request):

		try:
			estado_pendiente = Estado_Consulta.objects.get(nombre = 'Pendiente')
			estado_espera = Estado_Consulta.objects.get(nombre__icontains = 'En espera')

			servicios_atender = Servicio_Consultas.objects.select_related('paciente').filter(
				Q(estado_consulta = estado_espera) | Q(estado_consulta = estado_pendiente)
			)
			
			listaFumadores = []
			for serv_atencion in servicios_atender:
				if serv_atencion.paciente.get_servicio_requerido() == "Urgencias":
					if serv_atencion.paciente.get_tipo_paciente() == "joven":
						#print(serv_atencion.paciente)
						if Control_Joven.objects.get(paciente_id = serv_atencion.paciente.id).fuma:
							listaFumadores.append(serv_atencion.paciente)

			if len(listaFumadores)>0:
				serializer_class = PacienteNombreSerializer (listaFumadores, many = True)
				return Response(serializer_class.data, status.HTTP_200_OK)

			return Response({
			'error': 'No encontrados pacientes fumadores para urgencias'
			},status = status.HTTP_404_NOT_FOUND)

		except Exception as e:
			return {
				'state': False,
				'message': 'Fumadores_Urgentes: ' + str(e)
			}

class Pacientes_APIView(APIView):
	def get(self, request):
		#import ipdb; ipdb.set_trace()
		pacientes = Paciente.objects.all()
		serializer_class = PacienteSerializer (pacientes, many = True)
		return Response(serializer_class.data)


class get_Atender_Paciente_APIView(APIView):
	"""
	Se verifican uno a uno los pacientes y de acuerdo a reglas se clasifica segun servicio 
	"""

	def get(self, request):
		context = atenderPaciente()

		if context['state']:
			return Response({'message': context['message']},status = status.HTTP_200_OK)
		return Response({'message': context['message']},status = status.HTTP_500_INTERNAL_SERVER_ERROR)


def atenderPaciente():
	calcularPrioridadPacientes_ingresoSalaPendientes()
	try:
		estado_pendiente = Estado_Consulta.objects.get(nombre = 'Pendiente')
		estado_desocupada = Estado_Consulta.objects.get(nombre = 'Desocupada')
		estado_ocupada = Estado_Consulta.objects.get(nombre = 'Ocupada')
		estado_espera = Estado_Consulta.objects.get(nombre__icontains = 'En espera')

		#El ordenamiento por prioridad y llegada se hace desde el modelo paciente
		servicios_espera = Servicio_Consultas.objects.select_related('paciente').filter(
			estado_consulta = estado_espera).order_by('paciente')
		if servicios_espera.exists():
			servicios_atender = servicios_espera
			es_pendiente = False
		else:
			servicios_atender = Servicio_Consultas.objects.select_related('paciente').filter(
				estado_consulta = estado_pendiente).order_by('paciente')
			es_pendiente = True

		entran_atencion = 0
		entran_espera = 0
		continuan_espera = 0

		for serv_atencion in servicios_atender:
			sServicio = serv_atencion.paciente.get_servicio_requerido()
			servicio = Servicio.objects.get(nombre = sServicio)
			#print(f"Paciente {serv_atencion.paciente} ")
			if Servicio_Consultas.objects.filter(servicio = servicio, estado_consulta = estado_desocupada).exists(): 
				servicio_desocupado = Servicio_Consultas.objects.filter(servicio = servicio, estado_consulta = estado_desocupada).first() 
				servicio_desocupado.paciente = serv_atencion.paciente
				servicio_desocupado.estado_consulta = estado_ocupada
				servicio_desocupado.save()
				serv_atencion.delete()
				entran_atencion += 1
			elif es_pendiente:
				serv_atencion.estado_consulta = estado_espera
				serv_atencion.save(update_fields = ['estado_consulta'])
				entran_espera += 1
			else:
				continuan_espera += 1 

		return {
			'state': True,
			'message': 'Ingresan a Consulta: ' + str(entran_atencion) 
			+ '. Ingresan a Sala de Espera: ' + str(entran_espera) 
			+ '. Continuan en Espera: ' + str(continuan_espera) 
		}


	except Exception as e:
		return {
			'state': False,
			'message': 'Atender_Paciente: ' + str(e)
		}

def calcularPrioridadPacientes_ingresoSalaPendientes():
	"""
	Calcula prioridad y coloca al paciente en sala de pendientes
	prioridad = 0 -> No se ha calculado la prioridad
	"""
	pacientes = Paciente.objects.filter(prioridad = 0)
	for paciente in pacientes:
		paciente.prioridad = paciente.get_prioridad()
		paciente.save(update_fields = ['prioridad'])

		estado = Estado_Consulta.objects.get(nombre = 'Pendiente')

		Servicio_Consultas.objects.create(
			estado_consulta = estado, 
			paciente = paciente, 
		)
