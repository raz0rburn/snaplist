#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import io
#print vm to string
import configparser

import re
#for Telegram
import telebot
from requests import get
import requests
import socket
import time
import datetime
import os
import sys
#for https connection
import ssl
#VMWare lib for python
from pyVmomi import vim
from sys import argv
configfname = sys.argv[2]
dcname = sys.argv[1]
print(configfname)
config = configparser.ConfigParser()
config.read(configfname)
try:
    from pyVim.connect import SmartConnect
except ImportError:
    from pyvim.connect import SmartConnect


s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE

connection = SmartConnect(**config["VSphere"],sslContext=s)


def get_all_vms():
    content = connection.content
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    return [VirtualMachine(managed_object_ref) for managed_object_ref in container.view]


class VirtualMachine:
    def __init__(self, machine_object):
        self.vm = machine_object
        #for item in self._snapshot_info():
        #    print(item)
        if len(self._snapshot_info())==2:
            self.snapshot_count, self.snapshot_size = self._snapshot_info()
        else:
            self.snapshot_size = self._snapshot_info()
            self.snapshot_count = "N/A"
    @property
    def name(self):
        return self.vm.name

    def _snapshot_info(self):
        try:
            disk_list = self.vm.layoutEx.file
            size = 0
            count = 0
            for disk in disk_list:
                if disk.type == 'snapshotData':
                    size += disk.size
                    count += 1
                ss_disk = re.search('0000\d\d', disk.name)
                if ss_disk:
                    size += disk.size
            return count, round(size / 1024**3,2)
        except Exception: 
            return "No data"

    def __repr__(self):
        return "{}  {}  {}".format(self.name, self.snapshot_size, self.snapshot_count)



def get_all_vms_snap():
    content = connection.content
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    return [managed_object_ref for managed_object_ref in container.view]

def get_last_snapshot(vm):
    try:
        #print(vm.snapshot.rootSnapshotList[-1].name)
        return vm.name,vm.snapshot.rootSnapshotList[-1].name
    except AttributeError:
        return None,None


bot = telebot.TeleBot(config["Telegram"]["TOKEN"])


def send_to_telegram(message):

    apiToken = config["Telegram"]["TOKEN"]
    chatID = config["Telegram"]["chat_id"]
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    print(apiURL)
    while True:
        try:
            response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
            print(response.text)
            break
        except Exception as e:
            print(e)
            import time
            time.sleep(60)

#send_to_telegram("test")


str_buf = io.StringIO()
vm_full_list = list()
print("date name size count")
for virtual_machine in get_all_vms():
    buf2=io.StringIO()
    print(virtual_machine,file=buf2)
    s = buf2.getvalue()
    buf2.close()
    s = s.split()
    vm_element = list()
    vm_element.append(s[0])
    vm_element.append(s[1])
    vm_element.append(s[2])
    vm_full_list.append(vm_element)
    




for vm in get_all_vms_snap():
    vm_name,vm_last_snapshot = get_last_snapshot(vm)
    if vm_last_snapshot != None: 
        for vm_element in vm_full_list:
            if vm_name == vm_element[0]:
                print("📸",vm_element[0],"'",vm_last_snapshot,"';","Size:",vm_element[1],"Mb;","Count:",vm_element[2],file=str_buf)
    
print(str_buf.getvalue())
if str_buf.getvalue() != "":
    send_to_telegram('📝 '+dcname+chr(10)+str_buf.getvalue())
else:
    send_to_telegram('📷 '+dcname+"🎉Снапшотов нет!")

str_buf.close()



