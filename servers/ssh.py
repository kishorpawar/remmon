from paramiko import client
import multiprocessing

from servers.models import Server

class SSH:
    
    def __init__(self, ip_add):
        # getting credentials from db
        server = Server.objects.get(ip_add=ip_add)
        # Let the user know we're connecting to the server
        print ("Connecting to server.")
        # Create a new SSH client
        self.client = client.SSHClient()
        # The following line is required if you want the script to be able to access a server that's not yet in the known_hosts file
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # Make the connection
        self.client.connect(server.ip_add, username=server.username, password=server.password, look_for_keys=False)

    def sendCommand(self, command):
        # Check if connection is made previously
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)
 
                    # return as string
                    return str(alldata)
        else:
            return "Connection not opened."


def get_uptime(ip_add):
    """
    Get uptime
    """
    try:
        command = 'cat /proc/uptime'

        uptime = SSH(ip_add)

        times = uptime.sendCommand(command)
        uptime_seconds = float(times.split()[0])
        uptime_time = str(timedelta(seconds=uptime_seconds))
        data = uptime_time.split('.', 1)[0]

    except Exception as err:
        data = str(err)

    return data



def get_ipaddress(ip_add):
    """
    Get the IP Address
    """
    data = []
    try:
        eth = "ip addr | grep LOWER_UP | awk '{print $2}'"
        client = SSH(ip_add)

        iface = client.sendCommand(eth).strip().replace(':', '').split('\n')
        
        del iface[0]

        for i in iface:
            pipe = "ip addr show " + i + "| awk '{if ($2 == \"forever\"){!$2} else {print $2}}'"
            pipe = client.sendCommand(pipe)
            data1 = pipe.strip().split('\n')
            if len(data1) == 2:
                data1.append('unavailable')
            if len(data1) == 3:
                data1.append('unavailable')
            data1[0] = i
            data.append(data1)

        ips = {'interface': iface, 'itfip': data}

        data = ips

    except Exception as err:
        data = str(err)

    return data

def get_cpus(ip_add):
    """
    Get the number of CPUs and model/type
    """
    try:
        client = SSH(ip_add)

        model = "cat /proc/cpuinfo | grep 'model name'"
        pipe = client.sendCommand(model)
        data = pipe.strip().split(':')[-1]
        
        if not data:
            processor = "cat /proc/cpuinfo | grep 'Processor'"
            pipe = client.sendCommand(processor)
            data = pipe.strip().split(':')[-1]

        cpus = multiprocessing.cpu_count()

        data = {'cpus': cpus, 'type': data}

    except Exception as err:
        data = str(err)

    return data


def get_users(ip_add):
    """
    Get the current logged in users
    """
    try:
        client = SSH(ip_add)

        users = "who | awk '{print $1, $2, $6}'"
        users_list = client.sendCommand(users)
        data = users_list.strip().split('\n')
        
        if data == [""]:
            data = None
        else:
            data = [i.split(None, 3) for i in data]

    except Exception as err:
        data = str(err)

    return data


def get_traffic(ip_add, iface):
    """
    Get the traffic for the specified interface
    """
    try:
        client = SSH(ip_add)
        packets = "cat /proc/net/dev | grep " + iface + "| awk '{print $1, $9}'"
        packets = client.sendCommand(packets)

        data = packets.strip().split(':', 1)[-1]
        

        if not data[0].isdigit():
            packets = "cat /proc/net/dev | grep " + iface + "| awk '{print $2, $10}'"
            packets = client.sendCommand(packets)
            data = packets.strip().split(':', 1)[-1]

        data = data.split()

        traffic_in = int(data[0])
        traffic_out = int(data[1])

        all_traffic = {'traffic_in': traffic_in, 'traffic_out': traffic_out}
        data = all_traffic

    except Exception as err:
        data = str(err)

    return data


def get_disk(ip_add):
    """
    Get disk usage
    """
    try:
        client = SSH(ip_add)
        fs = "df -Ph | grep -v Filesystem | awk '{print $1, $2, $3, $4, $5, $6}'"
        fs = client.sendCommand(fs)
        data = fs.strip().split('\n')
        
        data = [i.split(None, 6) for i in data]

    except Exception as err:
        data = str(err)

    return data


def get_disk_rw(ip_add):
    """
    Get the disk reads and writes
    """
    try:
        client = SSH(ip_add)
        partitions = "cat /proc/partitions | grep -v 'major' | awk '{print $4}'"
        partitions = client.sendCommand(partitions)
        data = partitions.strip().split('\n')

        rws = []
        for part in data:
            if part.isalpha():
                stats = "cat /proc/diskstats | grep -w '" + part + "'|awk '{print $4, $8}'"
                stats = client.sendCommand(stats)
                rw = stats.strip().split()
                
                rws.append([part, rw[0], rw[1]])

        if not rws:
            stats = "cat /proc/diskstats | grep -w '" + data[0] + "'|awk '{print $4, $8}'"
            stats = client.sendCommand(stats)
            rw = stats.strip().split()
            
            rws.append([data[0], rw[0], rw[1]])

        data = rws

    except Exception as err:
        data = str(err)

    return data


def get_mem(ip_add):
    """
    Get memory usage
    """
    try:
        client = SSH(ip_add)
        mem = "free -tm | grep 'Mem' | awk '{print $2,$4,$6,$7}'"
        mem = client.sendCommand(mem)
        data = mem.strip().split()
        
        allmem = int(data[0])
        freemem = int(data[1])
        buffers = int(data[2])
        cachedmem = int(data[3])

        # Memory in buffers + cached is actually available, so we count it
        # as free.
        freemem += buffers + cachedmem

        percent = (100 - ((freemem * 100) / allmem))
        usage = (allmem - freemem)

        mem_usage = {'usage': usage, 'buffers': buffers, 'cached': cachedmem, 'free': freemem, 'percent': percent}

        data = mem_usage

    except Exception as err:
        data = str(err)

    return data


def get_cpu_usage(ip_add):
    """
    Get the CPU usage and running processes
    """
    try:
        client = SSH(ip_add)
        cpu = "ps aux --sort -%cpu,-rss"
        cpu = client.sendCommand(cpu)
        data = cpu.strip().split('\n')
        
        usage = [i.split(None, 10) for i in data]
        del usage[0]

        total_usage = []

        for element in usage:
            usage_cpu = element[2]
            total_usage.append(usage_cpu)

        total_usage = sum(float(i) for i in total_usage)

        total_free = ((100 * int(get_cpus(ip_add)['cpus'])) - float(total_usage))

        cpu_used = {'free': total_free, 'used': float(total_usage), 'all': usage}

        data = cpu_used

    except Exception as err:
        data = str(err)

    return data

def get_netstat(ip_add):
    """
    Get ports and applications
    """
    try:
        client = SSH(ip_add)
        ss = "ss -tnp | grep ESTAB | awk '{print $4, $5}'| sed 's/::ffff://g' \
        | awk -F: '{print $1, $2}' | awk 'NF > 0' | sort -n | uniq -c"

        ss = client.sendCommand(ss)
        data = ss.strip().split('\n')
        
        data = [i.split(None, 4) for i in data]

    except Exception as err:
        data = str(err)

    return data
