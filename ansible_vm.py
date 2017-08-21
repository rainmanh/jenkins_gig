#!/usr/bin/env python

import requests
import time
import os
import sys
from pexpect import pxssh

execfile("python_variables.txt")

headers = {'Authorization': str('Bearer ' + jwt_token), 'Content-type': 'application/json'}

def create_vm():
    params = {'cloudspaceId': vm_cloudspaceId,'name': vm_name,'sizeId': vm_sizeId,'imageId': vm_imageId,'disksize': vm_disksize }
    vm_id = requests.post(BASE_URL + 'cloudapi/machines/create',params=params,headers=headers).json()

    if vm_id == "Selected name already exists":
        print ("Selected name already exists!!")
        sys.exit(1)
    else:
        print ("VM_ID=" + str(vm_id))
    return  vm_id

def get_password_ip(vm_id):
    params = { 'machineId': vm_id }
    vm_pwd = requests.post(BASE_URL + 'cloudapi/machines/get',params=params,headers=headers).json()

    for accounts in vm_pwd['accounts']:
        vm_password = accounts['password']

    for item in vm_pwd['interfaces']:
        vm_ip = item['ipAddress']
        #print (vm_ip)

    return vm_password,vm_ip

def ip_wait(vm_id):
    while True:
        password,ip = get_password_ip(vm_id)
        if ip == "Undefined":
            time.sleep(2)
            print ("Waiting for the DHCP Server to lease an IP to the VM...")
        else:
            run_ansible()
            sys.exit(1)

def run_ansible():
    password,ip = get_password_ip(vm_id)
    print ("The VM got IP=" + ip)
    print ("Installing Python...")
    #Ensure sshd is up and running and Can access the internet
    time.sleep(20)

    try:
        ssh = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
        ssh.force_password = True
        ssh.login(ip, user_name, password, auto_prompt_reset=False)
        cmd1 = "if [ ! -f /etc/redhat-release ]; then echo " + password + " | sudo -S apt-get install python -y; fi"
        ssh.sendline(cmd1)
        #ssh.prompt()
        print(ssh.before)
        cmd2 = "if [ -f /etc/redhat-release ]; then echo " + password + " | sudo -S yum install python -y; fi"
        ssh.sendline(cmd2)
        #ssh.prompt()
        print(ssh.before)
        ssh.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(e)
        sys.exit(1)


    print ("Preparing Ansible Hosts File...")
    os.system('cp hosts_tpl hosts; echo %s >> hosts'  % ip)

    print ("Executing Ansible Command...")
    print ('ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook main.yml -i hosts -l gig_prod --user=%s --extra-vars "ansible_ssh_pass=Password ansible_sudo_pass=Password" -vv' % (user_name))
    os.system('ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook main.yml -i hosts -l gig_prod --user=%s --extra-vars "ansible_ssh_pass=%s ansible_sudo_pass=%s" -vv'  % (user_name, password, password))

vm_id = create_vm()
ip_wait(vm_id)
