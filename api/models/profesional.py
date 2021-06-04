from django.db import models

class Profesional(models.Model):
	nombre = models.CharField(max_length=50, blank=False, null=False)

	class Meta:
		ordering = ['nombre']

	def __str__(self):
		return '{} {} {} '.format(self.id, self.nombre, self.servicio)
