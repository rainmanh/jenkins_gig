#!/usr/bin/env python3

from aysclient.client import Client
from js9 import j
from jinja2 import Environment, FileSystemLoader
import requests
import time
import os
import sys
from pexpect import pxssh
import pprint

exec(open("python_variables.txt").read())
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_yaml_python(BASE_URL,jwt_token,vm_location,vm_vdc,account_name,vm_name,vm_disksize,vm_osimage,vm_memory):
    fname = "create_vm.yaml"
    context = {
    '__BASE_URL__': BASE_URL,
    '__JWT_TOKEN__': jwt_token,
    '__VM_LOCATION__': vm_location,
    '__VM_VDC__': vm_vdc,
    '__ACCOUNT_NAME__': account_name,
    '__VM_NAME__': vm_name,
    '__BOOT_DISK_SIZE__': vm_disksize,
    '__VM_MEMORY__': vm_memory,
    '__OS_IMAGE__': vm_osimage
    }
    #
    with open(fname, 'w') as f:
        yaml_file = render_template('create_vm.yaml_tpl', context)
        f.write(yaml_file)
        f.close()

def create_yaml_ansible(vm_login):

    #Remove file if exists.
    list_files = ['vars/main_head.yml','vars/main.yml']
    for old_files in list_files:
        if os.path.isfile(old_files):
            os.remove(old_files)

    fname = "vars/main_head.yml"
    context = {
    '__VM_LOGIN__': vm_login
    }
    #
    with open(fname, 'w') as f:
        yaml_file = render_template('main.yml_tpl', context)
        f.write(yaml_file)
        f.close()

    body_file = open("vars/main_body.yml_tpl", "r")
    head_yaml = open("vars/main_head.yml", "r")
    main_file = open("vars/main.yml", "a")

    for line in body_file:
        main_file.write(line.rstrip() + '\n' )
        for line in head_yaml:
            main_file.write(line.rstrip() + '\n' )

    head_yaml.close()
    body_file.close()
    main_file.close()

def create_vm():
    client = Client(ays_client)
    blueprint_file = open(file_name,'r')
    blueprint = blueprint_file.read()
    cl = j.clients.atyourservice.get().api.ays

    data = {'name': file_name, 'content':blueprint}
    #print(str(data))
    try:
      bp = client.ays.createBlueprint(data, repo_name)
      bp = client.ays.executeBlueprint('',file_name, repo_name)

      run = cl.createRun('', repo_name)
      run = cl.executeRun(repository=repo_name, data=None, runid=run.json()['key']).json()
      run = cl.getRun(repository=repo_name, runid=run['key']).json()
      while run['state'] != 'ok':
          time.sleep(2)
          run = cl.getRun(repository=repo_name, runid=run['key']).json()
          rv = cl.getServiceByName(role="node", name=vm_name, repository=repo_name).json()

      vm_id = rv['data']['machineId']
      vm_passwd = str(rv['data']['sshPassword'])
      vm_pub_ip = str(rv['data']['ipPublic'])
      vm_port = str(rv['data']['sshPort'])
      vm_login = str(rv['data']['sshLogin'])

      return {'vm_id':vm_id, 'vm_passwd':vm_passwd ,'vm_pub_ip':vm_pub_ip,'vm_port':vm_port,'vm_login':vm_login}

    except Exception as e:
        print("Error Provisioning!!")
        print(e)
        sys.exit(1)

def run_ansible(vm_passwd,vm_pub_ip,vm_port,vm_login):

    #Preparing the vars/main.yml file for the Ansible deployment
    print ("Preparing the vars/main.yml file for the Ansible deployment")
    create_yaml_ansible(vm_login)

    print ("Installing Python...")
    #Ensure sshd is up and running and Can access the internet
    #time.sleep(20)

    try:
      ssh = pxssh.pxssh(options={"StrictHostKeyChecking": "no","UserKnownHostsFile": "/dev/null"})
      ssh.force_password = True
      ssh.login(vm_pub_ip, vm_login, vm_passwd, auto_prompt_reset=False,port=vm_port)
      cmd1 = "if [ ! -f /etc/redhat-release ]; then echo " + vm_passwd + " | sudo -S apt-get install python -y; fi"
      ssh.sendline(cmd1)
      #ssh.prompt()
      print(ssh.before)
      cmd2 = "if [ -f /etc/redhat-release ]; then echo " + vm_passwd + " | sudo -S yum install python -y; fi"
      ssh.sendline(cmd2)
      #ssh.prompt()
      print(ssh.before)
      ssh.logout()
    except pxssh.ExceptionPxssh as e:
      print("pxssh failed on login.")
      print(e)
      sys.exit(1)

    print ("Preparing Ansible Hosts File...")
    os.system('cp hosts_tpl hosts; echo %s:%s >> hosts'  % (vm_pub_ip, vm_port))

    print ("Executing Ansible Command...")
    print ('ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook main.yml -i hosts -l gig_prod --user=%s --extra-vars "ansible_ssh_pass=Password ansible_sudo_pass=Password" -vv' % (vm_login))
    os.system('ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook main.yml -i hosts -l gig_prod --user=%s --extra-vars "ansible_ssh_pass=%s ansible_sudo_pass=%s" -vv'  % (vm_login, vm_passwd, vm_passwd))

def main():
    create_yaml_python(BASE_URL,jwt_token,vm_location,vm_vdc,account_name,vm_name,vm_disksize,vm_osimage,vm_memory)
    vm_data = create_vm()
    run_ansible(vm_data['vm_passwd'],vm_data['vm_pub_ip'],vm_data['vm_port'],vm_data['vm_login'])
    print("Jenkins is at: http://" + vm_data['vm_pub_ip'] + ":8080")

########################################

if __name__ == "__main__":
    main()
