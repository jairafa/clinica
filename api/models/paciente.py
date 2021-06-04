from django.db import models

class Paciente(models.Model):
	nombre = models.CharField(max_length=50, blank=False, null=False)
	edad = models.PositiveIntegerField(blank=False, null=False)
	historia = models.IntegerField(blank=False, null=False)
	prioridad = models.IntegerField(blank=True, null=True, default=0)


	class Meta:
		ordering = ['-prioridad','id']

	def __str__(self):
		return '{} {} edad {} historia {} tipo_paciente {} riesgo {} prioridad {} servicio {}'.format(
			self.id, self.nombre, self.edad , self.historia, self.get_tipo_paciente(), self.get_riesgo(), self.get_prioridad(), self.get_servicio_requerido())

	def get_tipo_paciente(self):
		if self.edad < 16:
			return "niño"
		elif self.edad < 41:
			return "joven"
		else: 
			return "anciano"

	def get_prioridad(self):
		if self.get_tipo_paciente() == "niño":
			control = Control_Ninno.objects.get(paciente_id = self.id)
		elif self.get_tipo_paciente() == "joven":
			control = Control_Joven.objects.get(paciente_id = self.id)
		else:#anciano
			control = Control_Anciano.objects.get(paciente_id = self.id)
		prioridad = control.get_prioridad() 
		return round(prioridad,2)


	def get_riesgo(self):
		if self.get_tipo_paciente() == "niño":
			control = Control_Ninno.objects.get(paciente_id = self.id)
			riesgo = control.get_prioridad() * self.edad / 100 + 0.0
		elif self.get_tipo_paciente() == "joven":
			control = Control_Joven.objects.get(paciente_id = self.id)
			riesgo = control.get_prioridad() * self.edad / 100 + 0.0
		else:#anciano
			control = Control_Anciano.objects.get(paciente_id = self.id)
			riesgo = control.get_prioridad() * self.edad / 100 + 5.3
		return round(riesgo,2)

	def get_servicio_requerido(self):
		servicio_requerido = ""
		if self.get_prioridad() > 4:
			servicio_requerido = "Urgencias"
		elif self.get_tipo_paciente() == "niño":
			servicio_requerido = "Pediatría"
		else:
			servicio_requerido = "Medicina Integral"
		return servicio_requerido


class Control_Ninno(models.Model):
	RELACION_CHOICES = (
		('1', '1-NORMAL'),
		('2', '2-BAJO PESO'),
		('3', '3-DESNUTRIDO'),
		('4', '4-SOBREPESO'),
	)	
	paciente = models.OneToOneField(Paciente, models.DO_NOTHING, blank=False, null=False)
	#relacion_peso_estatura = models.IntegerField(blank=False, null=False)
	relacion_peso_estatura = models.CharField(
		'Relacion Peso Estatura', 
		max_length=1, 
		choices=RELACION_CHOICES
	)	

	def __str__(self):
		return '{} Relacion Peso Estatura {}  Prioridad {} '.format(self.paciente, self.relacion_peso_estatura, self.get_prioridad())


	def get_prioridad(self):
		if self.paciente.edad < 6:
			return int(self.relacion_peso_estatura) + 3
		elif self.paciente.edad < 13:
			return int(self.relacion_peso_estatura) + 2
		elif self.paciente.edad < 16:
			return int(self.relacion_peso_estatura) + 1
		return 0


class Control_Joven(models.Model):
	paciente = models.OneToOneField(Paciente, models.DO_NOTHING, blank=False, null=False)
	fuma = models.BooleanField(default=False, blank=False, null=False)
	annios_fumando = models.IntegerField(blank=True, null=True) 

	def __str__(self):
		return '{} fuma {} Años fumando {} Prioridad {} '.format(self.paciente, self.fuma, self.annios_fumando, self.get_prioridad())

	def get_prioridad(self):
		if self.fuma:
			return int(round(self.annios_fumando/4 + 2))
		return 2

class Control_Anciano(models.Model):
	paciente = models.OneToOneField(Paciente, models.DO_NOTHING, blank=False, null=False)
	dieta_asignada = models.BooleanField(default=False, blank=False, null=False)

	def __str__(self):
		return '{} Tiene dieta_asignada {} Prioridad {}'.format(self.paciente, self.dieta_asignada, self.get_prioridad() )

	def get_prioridad(self):
		edad = self.paciente.edad
		if self.dieta_asignada and edad >= 60 and edad <= 100:
			return int(round(edad/20 + 4))
		return int(round(edad/30 + 3))
