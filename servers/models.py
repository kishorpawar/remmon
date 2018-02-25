# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Server(models.Model):
	name = models.CharField(max_length=100)
	ip_add = models.GenericIPAddressField()
	port = models.PositiveSmallIntegerField()
	username = models.CharField(max_length=128)
	password = models.CharField(max_length=128)
	enrolled_on = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.name

