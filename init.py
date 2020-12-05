#!/usr/bin/env python

from prometheus_client import start_http_server, Summary, Gauge, Enum
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import random
import time 
import datetime
import requests
import json
import urllib3

# Disable TLS Warning, cause of selfsigned cert
urllib3.disable_warnings()

baseUrl = "https://localhost:35113/api"
sessionStart = "/sessions/start"
sessionEnd = "/sessions/end"
listVms = "/vms/list"

with open('config.json') as config_file:
    data = json.load(config_file)

def altaro_login():
    #print("Logging in as: " + str(data['Username']))
    response = requests.post(baseUrl + sessionStart, json=data, verify=False)

    global sessionId
    sessionId = json.loads(response.text)['Data']
    #print("Logged in with SessionId: " + str(sessionId))

def altaro_logoff():
    #print("Logging off all sessions")
    requests.get(baseUrl + sessionEnd, verify=False)


def register_metrics():
    # register gauges

    global gauge_lastbackup
    global gauge_lastoffsitecopy
    global gauge_lastbackup_duration
    global gauge_lastoffsitecopy_duration
    global gauge_lastbackup_transfersize_compressed
    global gauge_lastbackup_transfersize_uncompressed
    global gauge_lastoffsitecopy_transfersize_compressed
    global gauge_lastoffsitecopy_transfersize_uncompressed
    global enum_lastbackup_result
    global enum_lastoffsitecopy_result
    
    gauge_lastbackup = Gauge('altaro_lastbackup_timestamp','Timestamp of last backup', ['vmname', 'hostname', 'vmuuid'])
    gauge_lastoffsitecopy = Gauge('altaro_lastoffsitecopy_timestamp','Timestamp of last offsite copy', ['vmname', 'hostname', 'vmuuid'])

    gauge_lastbackup_duration = Gauge('altaro_lastbackup_duration_seconds','Duration of last backup', ['vmname', 'hostname', 'vmuuid'])
    gauge_lastoffsitecopy_duration = Gauge('altaro_lastoffsitecopy_duration_seconds','Duration of last offsite copy', ['vmname', 'hostname', 'vmuuid'])

    gauge_lastbackup_transfersize_compressed = Gauge('altaro_lastbackup_transfersize_compressed_bytes','Compressed size of last backup', ['vmname', 'hostname', 'vmuuid'])
    gauge_lastbackup_transfersize_uncompressed = Gauge('altaro_lastbackup_transfersize_uncompressed_bytes','Unompressed size of last backup', ['vmname', 'hostname', 'vmuuid'])

    gauge_lastoffsitecopy_transfersize_compressed = Gauge('altaro_lastoffsitecopy_transfersize_compressed_bytes','Compressed size of last offsite copy', ['vmname', 'hostname', 'vmuuid'])
    gauge_lastoffsitecopy_transfersize_uncompressed = Gauge('altaro_lastoffsitecopy_transfersize_uncompressed_bytes','Uncompressed size of last offsite copy', ['vmname', 'hostname', 'vmuuid'])

    enum_lastbackup_result = Enum('altaro_lastbackup_result','Result of last backup', ['vmname', 'hostname', 'vmuuid'], states=['Success', 'Warning', 'Error'])
    enum_lastoffsitecopy_result = Enum('altaro_lastoffsitecopy_result','Result of last offsite copy', ['vmname', 'hostname', 'vmuuid'], states=['Success', 'Warning', 'Error'])

def altaro_listvm():
    response = requests.get(baseUrl + listVms + '/' + sessionId, verify=False)
    vmlist = json.loads(response.text)

    global vms
    vms = vmlist['VirtualMachines']

    for vm in range(len(vms)):
        vmname = vms[vm]['VirtualMachineName']
        hostname = vms[vm]['HostName']
        vmuuid = vms[vm]['HypervisorVirtualMachineUuid']

        #Last Backup
        string = vms[vm]['LastBackupTime']
        timestamp = float(time.mktime(datetime.datetime.strptime(string, "%Y-%m-%d-%H-%M-%S").timetuple()))
        
        gauge_lastbackup.labels(vmname, hostname, vmuuid).set(timestamp)

        #Last Offsite Copy
        string = vms[vm]['LastOffsiteCopyTime']
        timestamp = float(time.mktime(datetime.datetime.strptime(string, "%Y-%m-%d-%H-%M-%S").timetuple()))
        
        gauge_lastoffsitecopy.labels(vmname, hostname, vmuuid).set(timestamp)

        #LastBackupDuration in Seconds
        gauge_lastbackup_duration.labels(vmname, hostname, vmuuid).set(vms[vm]['LastBackupDuration'])

        #LastOffsiteCopyDuration in Seconds
        gauge_lastoffsitecopy_duration.labels(vmname, hostname, vmuuid).set(vms[vm]['LastOffsiteCopyDuration'])

        #LastOffsiteCopyTransferSizeCompressed in Bytes
        gauge_lastoffsitecopy_transfersize_compressed.labels(vmname, hostname, vmuuid).set(vms[vm]['LastOffsiteCopyTransferSizeCompressed'])

        #LastOffsiteCopyTransferSizeUncompressed in Bytes
        gauge_lastoffsitecopy_transfersize_uncompressed.labels(vmname, hostname, vmuuid).set(vms[vm]['LastOffsiteCopyTransferSizeUncompressed'])

        #LastBackupTransferSizeCompressed in Bytes
        gauge_lastbackup_transfersize_compressed.labels(vmname, hostname, vmuuid).set(vms[vm]['LastBackupTransferSizeCompressed'])

        #LastBackupTransferSizeUncompressed in Bytes
        gauge_lastbackup_transfersize_uncompressed.labels(vmname, hostname, vmuuid).set(vms[vm]['LastBackupTransferSizeUncompressed'])

        #LastBackupResult
        enum_lastbackup_result.labels(vmname, hostname, vmuuid).state(vms[vm]['LastBackupResult'])

        #LastOffsiteCopyResult
        enum_lastoffsitecopy_result.labels(vmname, hostname, vmuuid).state(vms[vm]['LastOffsiteCopyResult'])
                 

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

if __name__ == '__main__':
    print("Altaro Backup Exporter")
    print("2020 - raphii / Raphael Pertl")
    # POST Login to Altaro REST API
    altaro_login()
    # register metrics
    register_metrics()
    # GET VM List
    altaro_listvm()
    # Start up the server to expose the metrics.
    start_http_server(int(data['ExporterPort']))
    print("Web Server running on Port " + str(data['ExporterPort']))
    
    altaro_logoff()
    while True:
        process_request(random.random())
        altaro_login()
        altaro_listvm()
        altaro_logoff()
