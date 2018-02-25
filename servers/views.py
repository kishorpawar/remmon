# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict

from models import Server

from servers.serializers import ServerSerializer
# Create your views here.


class HomeView(TemplateView):
	template_name = "home.html"

class EnrollView(View):
	
	def post(self, request, *args, **kwargs):

		print request.POST
		try:
			server, created = Server.objects.get_or_create(
				ip_add = request.POST.get('ip_add'),
				username = request.POST.get("username"),
				defaults={
						'name' : request.POST.get('server_name'),
						'port' : request.POST.get("ssh_port"),
						'password' : request.POST.get("password"),
						}
				)

			if created:
				server.save()
				return JsonResponse(model_to_dict(server), status=200)
			else:
				return HttpResponse(status=302)
		except Exception as e:
			print e
			return HttpResponse(status=500) 




class ServerViewSet(viewsets.ModelViewSet):
	"""
		APi endpoint that allows servers to be viewed or Edited. 
		Also, it lets to add entry into server model
	"""

	serializer_class = ServerSerializer
	queryset = Server.objects.all().order_by('-enrolled_on')