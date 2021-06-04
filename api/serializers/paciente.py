from rest_framework import serializers

from api.models.paciente import *


class PacienteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Paciente
		# fields = ['nombre', 'edad', 'historia']
		fields = '__all__'

class PacienteNombreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Paciente
		fields = ['nombre']

