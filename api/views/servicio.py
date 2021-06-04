from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count, Max


from api.models.paciente import *
from api.models.servicio import *
from api.views.paciente import atenderPaciente


class get_Liberar_Consultas_APIView(APIView):
	"""
	Libera (Desocupa) todas las consultas que están ocupadas en el Hospital 
	Ejecuta la funcionalidad de Atender Paciente
	"""

	def get(self, request):

		estado_desocupada = Estado_Consulta.objects.get(nombre = 'Desocupada')
		estado_ocupada = Estado_Consulta.objects.get(nombre = 'Ocupada')
		estado_atendido = Estado_Consulta.objects.get(nombre = 'Atendido')


		cantidad = Servicio_Consultas.objects.filter(
			estado_consulta = estado_ocupada
		).count()


		Servicio_Consultas.objects.filter(
			estado_consulta = estado_ocupada
		).update(estado_consulta = estado_atendido)


		servicios = Servicio.objects.all()

		for servicio in servicios:
			Servicio_Consultas.objects.create(
				estado_consulta = estado_desocupada, 
				servicio = servicio, 
			)		


		context = atenderPaciente()

		if context['state']:
			return Response({'message': 'Se liberan ' + str(cantidad) + ' consultas. ' + context['message'] + '. '} 
				,status = status.HTTP_200_OK)
		return Response({'message': context['message']},status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class get_Consulta_mas_Pacientes_Atendidos_APIView(APIView):
	"""
	Muestra la consulta que más pacientes ha atendido hasta el momento del pedido
	"""

	def get(self, request):

		try:
			estado_atendido = Estado_Consulta.objects.get(nombre = 'Atendido')

			#Con esta funcionalidad solo se tiene un acceso a la base de datos
			#Ordena descendente por cantidad
			servicios_atendidos = Servicio_Consultas.objects.select_related('servicios').filter(
				estado_consulta = estado_atendido
			).values('servicio__nombre').annotate(
			Count('servicio__nombre')).order_by('-servicio__nombre__count')

			#print(f"servicios_atendidos {servicios_atendidos}")
			#print (f"****{servicios_atendidos[0]}")

			mas_atendidos = [] #Pueden existir varios servicios con la misma cantidad de pacientes atendidos
			iCuentaActual = 0
			iCuentaAnterior = 0
			for atendidos in servicios_atendidos:
				iCuentaActual = atendidos['servicio__nombre__count']
				if iCuentaActual >= iCuentaAnterior:
					iCuentaAnterior = iCuentaActual
					mas_atendidos.append(atendidos) 
				else:
					break

				#sServicio = atendidos['servicio__nombre']
				#iCuenta = atendidos['servicio__nombre__count']


			return Response(
				{'message': 'Los servicios con mas pacientes atendidos',
				 'mas_atendidos' : mas_atendidos
				} 
				,status = status.HTTP_200_OK)
		except Exception as e:
			return Response({'message': 'Error al encontrar el paciente mas atendido: ' + str(e)}
				,status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class get_Paciente_Mas_Anciano_APIView(APIView):
	"""
	De los pacientes que están en la sala de espera se obtiene el más anciano de todos.
	"""

	def get(self, request):

		try:
			estado_espera = Estado_Consulta.objects.get(nombre__icontains = 'En espera')


			#Con esta funcionalidad solo se tiene un acceso a la base de datos
			#Ordena descendente por cantidad
			servicios_espera = Servicio_Consultas.objects.select_related('paciente').filter(
				estado_consulta = estado_espera
				#,paciente__get_tipo_paciente = 'anciano'
			).aggregate(Max('paciente__edad'))

			#print(f"servicios_espera {servicios_espera}")
			#print (f"****{servicios_espera['paciente__edad__max']}")

			max_edad = servicios_espera['paciente__edad__max']

			servicios_edades = Servicio_Consultas.objects.select_related('paciente').filter(
				estado_consulta = estado_espera
				,paciente__edad = max_edad
			)

			mas_ancianos = [] #Pueden existir varios pacientes con la misma edad
			iCuentaActual = 0
			iCuentaAnterior = 0
			for servicio in servicios_edades:
				mas_ancianos.append({
					'nombre': servicio.paciente.nombre,
					'edad':servicio.paciente.edad
					}) 



			return Response(
				{'message': 'El paciente mas anciano',
				 'mas_ancianos' : mas_ancianos
				} 
				,status = status.HTTP_200_OK)
		except Exception as e:
			return Response({'message': 'Error al buscar al mas anciano: ' + str(e)}
				,status = status.HTTP_500_INTERNAL_SERVER_ERROR)

