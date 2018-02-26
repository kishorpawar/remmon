# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict

import json
from datetime import timedelta
import multiprocessing

from models import Server

from servers.serializers import ServerSerializer

from servers.ssh import *
# Create your views here.


time_refresh = 30000
time_refresh_long = 120000
time_refresh_net = 2000

class HomeView(TemplateView):
	template_name = "home.html"


# NOT IN USE NOW
class EnrollView(View):
	
	def post(self, request, *args, **kwargs):
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

			return HttpResponse(status=500) 




class ServerViewSet(viewsets.ModelViewSet):
	"""
		APi endpoint that allows servers to be viewed or Edited. 
		Also, it lets to add entry into server model
	"""

	serializer_class = ServerSerializer
	queryset = Server.objects.all().order_by('-enrolled_on')


def getnetstat(request):
    """
    Return netstat output
    """
    try:
        net_stat = get_netstat('192.168.0.243')
    except Exception:
        net_stat = None

    data = json.dumps(net_stat)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def getcpus(request, name):
    """
    Return the CPU number and type/model
    """
    cpus = get_cpus()
    cputype = cpus['type']
    cpucount = cpus['cpus']
    data = {}

    if name == 'type':
        try:
            data = cputype
        except Exception:
            data = None

    if name == 'count':
        try:
            data = cpucount
        except Exception:
            data = None

    data = json.dumps(data)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def uptime(request):
    """
    Return uptime
    """
    try:
        up_time = get_uptime()
    except Exception:
        up_time = None

    data = json.dumps(up_time)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def getdisk(request):
    """
    Return the disk usage
    """
    ip_add = request.GET.get('ip_add')
    try:
        diskusage = get_disk(ip_add)
    except Exception:
        diskusage = None

    data = json.dumps(diskusage)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def getips(request):
    """
    Return the IPs and interfaces
    """
    
    ip_add = request.GET.get('ip_add')

    try:
        get_ips = get_ipaddress(ip_add)
    except Exception:
        get_ips = None

    data = json.dumps(get_ips['itfip'])
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def getusers(request):
    """
    Return online users
    """
    ip_add = request.GET.get('ip_add')

    try:
        online_users = get_users(ip_add)
    except Exception:
        online_users = None

    data = json.dumps(online_users)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def getproc(request):
    """
    Return the running processes
    """
    ip_add = request.GET.get('ip_add')

    try:
        processes = get_cpu_usage(ip_add)
        processes = processes['all']
    except Exception:
        processes = None

    data = json.dumps(processes)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def cpuusage(request):
    """
    Return CPU Usage in %
    """
    ip_add = request.GET.get('ip_add')

    try:
        cpu_usage = get_cpu_usage(ip_add)
    except Exception as e:
        cpu_usage = 0

    cpu = [
        {
            "value": cpu_usage['free'],
            "color": "#0AD11B"
        },
        {
            "value": cpu_usage['used'],
            "color": "#F7464A"
        }
    ]

    data = json.dumps(cpu)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(data)
    return response


def memusage(request):
    """
    Return Memory Usage in % and numeric
    """
    datasets_free = []
    datasets_used = []
    datasets_buffers = []
    datasets_cached = []
    ip_add = request.GET.get('ip_add')

    try:
        mem_usage = get_mem(ip_add)
    except Exception as e:
        mem_usage = 0

    try:
        cookies = request.COOKIES['memory_usage']
    except Exception:
        cookies = None

    if not cookies:
        datasets_free.append(0)
        datasets_used.append(0)
        datasets_buffers.append(0)
        datasets_cached.append(0)
    else:
        datasets = json.loads(cookies)
        datasets_free = datasets[0]
        datasets_used = datasets[1]
        datasets_buffers = datasets[2]
        datasets_cached = datasets[3]

    if len(datasets_free) > 10:
        while datasets_free:
            del datasets_free[0]
            if len(datasets_free) == 10:
                break
    if len(datasets_used) > 10:
        while datasets_used:
            del datasets_used[0]
            if len(datasets_used) == 10:
                break
    if len(datasets_buffers) > 10:
        while datasets_buffers:
            del datasets_buffers[0]
            if len(datasets_buffers) == 10:
                break
    if len(datasets_cached) > 10:
        while datasets_cached:
            del datasets_cached[0]
            if len(datasets_cached) == 10:
                break
    if len(datasets_free) <= 9:
        datasets_free.append(int(mem_usage['free']))
    if len(datasets_free) == 10:
        datasets_free.append(int(mem_usage['free']))
        del datasets_free[0]
    if len(datasets_used) <= 9:
        datasets_used.append(int(mem_usage['usage']))
    if len(datasets_used) == 10:
        datasets_used.append(int(mem_usage['usage']))
        del datasets_used[0]
    if len(datasets_buffers) <= 9:
        datasets_buffers.append(int(mem_usage['buffers']))
    if len(datasets_buffers) == 10:
        datasets_buffers.append(int(mem_usage['buffers']))
        del datasets_buffers[0]
    if len(datasets_cached) <= 9:
        datasets_cached.append(int(mem_usage['cached']))
    if len(datasets_cached) == 10:
        datasets_cached.append(int(mem_usage['cached']))
        del datasets_cached[0]

    # Some fix division by 0 Chart.js
    if len(datasets_free) == 10:
        if sum(datasets_free) == 0:
            datasets_free[9] += 0.1
        if sum(datasets_free) / 10 == datasets_free[0]:
            datasets_free[9] += 0.1

    memory = {
        'labels': [""] * 10,
        'datasets': [
            {
                "fillColor": "rgba(247,70,74,0.5)",
                "strokeColor": "rgba(247,70,74,1)",
                "pointColor": "rgba(247,70,74,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_used
            },
            {
                "fillColor": "rgba(43,214,66,0.5)",
                "strokeColor": "rgba(43,214,66,1)",
                "pointColor": "rgba(43,214,66,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_free
            },
            {
                "fillColor": "rgba(0,154,205,0.5)",
                "strokeColor": "rgba(0,154,205,1)",
                "pointColor": "rgba(0,154,205,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_buffers
            },
            {
                "fillColor": "rgba(255,185,15,0.5)",
                "strokeColor": "rgba(255,185,15,1)",
                "pointColor": "rgba(265,185,15,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_cached
            }
        ]
    }

    cookie_memory = [datasets_free, datasets_used, datasets_buffers, datasets_cached]
    data = json.dumps(memory)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.cookies['memory_usage'] = cookie_memory
    response.write(data)
    return response


def gettraffic(request):
    """
    Return the traffic for the interface
    """
    datasets_in = []
    datasets_in_i = []
    datasets_out = []
    datasets_out_o = []
    label = "KBps"
    ip_add = request.GET.get('ip_add')

    try:
        intf = get_ipaddress(ip_add)
        intf = intf['interface'][0]

        traffic = get_traffic(ip_add, intf)
    except Exception as e:
    	traffic = 0

    try:
        cookies = request.COOKIES['traffic']
    except Exception:
        cookies = None

    if not cookies:
        datasets_in.append(0)
        datasets_in_i.append(0)
        datasets_out.append(0)
        datasets_out_o.append(0)
    else:
        datasets = json.loads(cookies)
        datasets_in = datasets[0]
        datasets_out = datasets[1]
        datasets_in_i = datasets[2]
        datasets_out_o = datasets[3]

    if len(datasets_in) > 10:
        while datasets_in:
            del datasets_in[0]
            if len(datasets_in) == 10:
                break
    if len(datasets_in_i) > 2:
        while datasets_in_i:
            del datasets_in_i[0]
            if len(datasets_in_i) == 2:
                break
    if len(datasets_out) > 10:
        while datasets_out:
            del datasets_out[0]
            if len(datasets_out) == 10:
                break
    if len(datasets_out_o) > 2:
        while datasets_out_o:
            del datasets_out_o[0]
            if len(datasets_out_o) == 2:
                break

    if len(datasets_in_i) <= 1:
        datasets_in_i.append(float(traffic['traffic_in']))
    if len(datasets_in_i) == 2:
        datasets_in_i.append(float(traffic['traffic_in']))
        del datasets_in_i[0]
    if len(datasets_out_o) <= 1:
        datasets_out_o.append(float(traffic['traffic_out']))
    if len(datasets_out_o) == 2:
        datasets_out_o.append(float(traffic['traffic_out']))
        del datasets_out_o[0]

    dataset_in = (float(((datasets_in_i[1] - datasets_in_i[0]) / 1024) / (time_refresh_net / 1000)))
    dataset_out = (float(((datasets_out_o[1] - datasets_out_o[0]) / 1024) / (time_refresh_net / 1000)))

    if dataset_in > 1024 or dataset_out > 1024:
        dataset_in = (float(dataset_in / 1024))
        dataset_out = (float(dataset_out / 1024))
        label = "MBps"

    if len(datasets_in) <= 9:
        datasets_in.append(dataset_in)
    if len(datasets_in) == 10:
        datasets_in.append(dataset_in)
        del datasets_in[0]
    if len(datasets_out) <= 9:
        datasets_out.append(dataset_out)
    if len(datasets_out) == 10:
        datasets_out.append(dataset_out)
        del datasets_out[0]

    # Some fix division by 0 Chart.js
    if len(datasets_in) == 10:
        if sum(datasets_in) == 0:
            datasets_in[9] += 0.1
        if sum(datasets_in) / 10 == datasets_in[0]:
            datasets_in[9] += 0.1

    traff = {
        'labels': [label] * 10,
        'datasets': [
            {
                "fillColor": "rgba(105,210,231,0.5)",
                "strokeColor": "rgba(105,210,231,1)",
                "pointColor": "rgba(105,210,231,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_in
            },
            {
                "fillColor": "rgba(227,48,81,0.5)",
                "strokeColor": "rgba(227,48,81,1)",
                "pointColor": "rgba(227,48,81,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_out
            }
        ]
    }

    cookie_traffic = [datasets_in, datasets_out, datasets_in_i, datasets_out_o]
    data = json.dumps(traff)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.cookies['traffic'] = cookie_traffic
    response.write(data)
    return response


def getdiskio(request):
    """
    Return the reads and writes for the drive
    """
    datasets_in = []
    datasets_in_i = []
    datasets_out = []
    datasets_out_o = []
    ip_add = request.GET.get('ip_add')

    try:
        diskrw = get_disk_rw(ip_add)
        diskrw = diskrw[0]
    except Exception:
        diskrw = 0

    try:
        cookies = request.COOKIES['diskrw']
    except Exception:
        cookies = None

    if not cookies:
        datasets_in.append(0)
        datasets_in_i.append(0)
        datasets_out.append(0)
        datasets_out_o.append(0)
    else:
        datasets = json.loads(cookies)
        datasets_in = datasets[0]
        datasets_out = datasets[1]
        datasets_in_i = datasets[2]
        datasets_out_o = datasets[3]

    if len(datasets_in) > 10:
        while datasets_in:
            del datasets_in[0]
            if len(datasets_in) == 10:
                break
    if len(datasets_in_i) > 2:
        while datasets_in_i:
            del datasets_in_i[0]
            if len(datasets_in_i) == 2:
                break
    if len(datasets_out) > 10:
        while datasets_out:
            del datasets_out[0]
            if len(datasets_out) == 10:
                break
    if len(datasets_out_o) > 2:
        while datasets_out_o:
            del datasets_out_o[0]
            if len(datasets_out_o) == 2:
                break

    if len(datasets_in_i) <= 1:
        datasets_in_i.append(int(diskrw[1]))
    if len(datasets_in_i) == 2:
        datasets_in_i.append(int(diskrw[1]))
        del datasets_in_i[0]
    if len(datasets_out_o) <= 1:
        datasets_out_o.append(int(diskrw[2]))
    if len(datasets_out_o) == 2:
        datasets_out_o.append(int(diskrw[2]))
        del datasets_out_o[0]

    dataset_in = (int((datasets_in_i[1] - datasets_in_i[0]) / (time_refresh_net / 1000)))
    dataset_out = (int((datasets_out_o[1] - datasets_out_o[0]) / (time_refresh_net / 1000)))

    if len(datasets_in) <= 9:
        datasets_in.append(dataset_in)
    if len(datasets_in) == 10:
        datasets_in.append(dataset_in)
        del datasets_in[0]
    if len(datasets_out) <= 9:
        datasets_out.append(dataset_out)
    if len(datasets_out) == 10:
        datasets_out.append(dataset_out)
        del datasets_out[0]

    # Some fix division by 0 Chart.js
    if len(datasets_in) == 10:
        if sum(datasets_in) == 0:
            datasets_in[9] += 0.1
        if sum(datasets_in) / 10 == datasets_in[0]:
            datasets_in[9] += 0.1

    disk_rw = {
        'labels': [""] * 10,
        'datasets': [
            {
                "fillColor": "rgba(245,134,15,0.5)",
                "strokeColor": "rgba(245,134,15,1)",
                "pointColor": "rgba(245,134,15,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_in
            },
            {
                "fillColor": "rgba(15,103,245,0.5)",
                "strokeColor": "rgba(15,103,245,1)",
                "pointColor": "rgba(15,103,245,1)",
                "pointStrokeColor": "#fff",
                "data": datasets_out
            }
        ]
    }

    cookie_diskrw = [datasets_in, datasets_out, datasets_in_i, datasets_out_o]
    data = json.dumps(disk_rw)
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.cookies['diskrw'] = cookie_diskrw
    response.write(data)
    return response