from django.db import models

from api.models.paciente import *
from api.models.profesional import *

#Ocupada, Desocupada ó En espera de atención al paciente
class Estado_Consulta(models.Model):
	nombre = models.CharField(max_length=50, blank=False, null=False)

	class Meta:
		ordering = ['nombre']

	def __str__(self):
		return '{} {} '.format(self.id, self.nombre)


#PEDIATRÍA, URGENCIAS ó MEDICINA INTEGRAL MI
class Servicio(models.Model):
	nombre = models.CharField(max_length=50, blank=False, null=False)
	profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, blank=True, null=True)


	consultas = models.ManyToManyField(
		Estado_Consulta,
		related_name = 'consultas',
		through='Servicio_Consultas',
		blank=True,
	)

	def __str__(self):
		return '{} {} '.format(self.id, self.nombre)



class Servicio_Consultas(models.Model):
	servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, blank=True, null=True)
	estado_consulta = models.ForeignKey(Estado_Consulta, on_delete=models.CASCADE, blank=False, null=False, default=2)
	paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return '{} {} {} {} '.format(self.id, self.servicio, self.estado_consulta , self.paciente)


