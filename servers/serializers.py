from rest_framework import serializers

from servers.models import Server



class ServerSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Server
		fields = ('name', 'ip_add', 'port', 'enrolled_on', 'username', 'password')