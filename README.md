[![Build Status](https://travis-ci.org/rainmanh/jenkins_gig.svg)](https://travis-ci.org/rainmanh/jenkins_gig)


Jenkins GIG Deployment
======================

This is a PoC for installing Jenkins using GIG Solutions.


I base the ansible code on Larry's solution (https://github.com/mrlesmithjr/ansible-jenkins) on what jenkins relate with some changes to it.
I am also adding a iptable role as I would like to add some extra security to this setup (the latest is not relevant for the Docker build).

There are 2 different proposed solutions:

 * ansible_vm.py
 * ays_vm.py


 These PoC includes:
  * Testing through Travis
  * Testing (ports) within the jenkins ansible role.


 # ansible_vm.py


The "base image" Selected for this Build is an "Ubuntu 16.04 x64". It hasn't been tested on any other distribution at the present.


Also *NOTE* this a a deployment for an Intranet, so you need the OpenVPN against your Cloud Space open for your deployment.

Requirements
------------

  You need the following:
   * python3
   * Ansible
   * sshpass
   * Python Libraries:
    * pexpect
    * jinja2


Instructions
------------

  * From your session just execute file *ansible_vm.py* against the GIG and python along with Ansible will do the rest!

  You got 2 set of variables:
  * ansible at vars/main.yml
  * python: python_variables.txt at the root directory.

 # ays_run.py

This script has been written to perform an AYS deployment.

This script has to be run in an environment with got all the JS9/AYS9 tools an libraries in it.

At the present it relies on the VM newly created to have a PUBLIC IP for the purposes of the Jenkins installation.

Requirements
------------

You need the following:
 * python3
 * Ansible
 * sshpass
 * Python Libraries:
  * pexpect
  * jinja2

Also, at the presentm you need a GIG Development environment in place and to have the G9 container built. (otherwise you can setup your environment in a different way...)
* https://github.com/Jumpscale/developer/blob/master/README.md
* https://github.com/Jumpscale/ays9/


This script will deploy 2 templates:

 * create_vm.yaml
 * vars/main.yml

 The location for the templates is the following:
 * templates/create_vm.yaml_tpl
 * templates/main.yaml_tpl

This script also assumes you got a VDC already defined.

Instructions
------------

* From your session just execute file *ays_run.py* against the GIG and python along with Ansible will do the rest!

The variables are in the following files:
 * python_variables.txt
 * vars/main_head.yml (these variables are for jenkins and they also need to be completed)

  Further Details
  ---------------

  Taking into account some security aspects, the Password Based VM will be modified so
  * the Password for the default user will be disabled
  * the sshd server will be restarted after NOT allowing Passworded Logins
  * Your local ssh key will be placed in the server (read vars/main.yml file), so you can log into the VM with the following command:

  ````
  ssh -i <private_ssh_key> cloudscalers@<_private_ip_>

  ````
  *Jenkins is by default running at port 8080*



  *http://_private_ip_:8080*

## Sources and Further reading

* jinja2 http://jinja.pocoo.org
* ansible https://www.ansible.com
* GIG AYS9 https://github.com/Jumpscale/ays9/
* GIG Developer https://github.com/Jumpscale/developer

