[![Build Status](https://travis-ci.org/rainmanh/jenkins_gig.svg)](https://travis-ci.org/rainmanh/jenkins_gig)


Jenkins GIG Deployment
======================

![gig_uk](https://github.com/rainmanh/jenkins_gig/blob/master/images/giguk3_new.png)

This is a PoC for installing Jenkins using GIG Solutions.


I base the ansible code on Larry's solution (https://github.com/mrlesmithjr/ansible-jenkins) on what jenkins relate with some changes to it.
I am also adding a iptable role as I would like to add some extra security to this setup (the latest is not relevant for the Docker build).

This PoC includes:
 * Testing through Travis
 * Testing (ports) within the jenkins ansible role.

The based image Selected for this Build is an "Ubuntu 16.04 x64". It hasn't been tested on any other distribution at the present.


Also *NOTE* this a a deployment for an Intranet, so you need the OpenVPN against your Cloud Space open for your deployment.

  Requirements
  ------------

  You need the following:
   * python
   * Ansible
   * Python Libraries:
    * pexpect


    Instructions
    ------------

  * From your session just execute file *ansible_vm.py* against the GIG and python along with Ansible will do the rest!

  You got 2 set of variables:
  * ansible at vars/main.yml
  * python: python_variables.txt at the root directory.


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


http://giguk.tech
