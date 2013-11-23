"""
Provides tools to deploy CodaLab.
"""
import base64
import logging
import logging.config
import os
import sys
import time
# Add codalabtools to the module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from azure import WindowsAzureMissingResourceError
from azure.servicemanagement import (ConfigurationSet,
                                     ConfigurationSetInputEndpoint,
                                     KeyPair,
                                     LinuxConfigurationSet,
                                     OSVirtualHardDisk,
                                     PublicKey,
                                     ServiceManagementService,
                                     ServiceBusManagementService)
from azure.storage import BlobService
from azure.servicebus import ServiceBusService

from codalabtools import BaseConfig

logger = logging.getLogger('codalabtools')

class DeploymentConfig(BaseConfig):
    """
    Defines credentials and configuration values needed to deploy CodaLab.
    """
    def __init__(self, label=None, filename='.codalabconfig'):
        super(DeploymentConfig, self).__init__(filename)

        self.label = label
        self._dinfo = self.info['deployment']
        self._azure_mgmt_info = self._dinfo['azure-management']
        self._svc_global = self._dinfo['service-global']
        self._bld = self._dinfo['build-configuration']
        self._svc = self._dinfo['service-configurations'][label] if label is not None else {}

    @staticmethod
    def _cap(word):
        """
        Returns a capitalized word.
        """
        return word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper()

    def getLoggerDictConfig(self):
        """Gets Dict config for logging configuration."""
        if 'logging' in self._dinfo:
            return self._dinfo['logging']
        else:
            return super(DeploymentConfig, self).getLoggerDictConfig()

    def getAzureSubscriptionId(self):
        """Gets the Azure Subscription ID."""
        return self._azure_mgmt_info['subscription-id']

    def getAzureCertificatePath(self):
        """Gets the path for the Azure Service Management certificate."""
        return self._azure_mgmt_info['certificate-path']

    def getAzureOperationTimeout(self):
        """
        Gets a duration (in seconds) to limit the time spent waiting for the completion
        of a long running operation in Azure.
        """
        return self._azure_mgmt_info['operation-timeout']

    def getServiceLocation(self):
        """Gets the name of the Azure region in which services will be deployed."""
        return self._svc_global['location']

    def getServicePrefix(self):
        """Gets the unique prefix used to build the name of services and other resources."""
        return self._svc_global['prefix']

    def getAffinityGroupName(self):
        """Gets the name of the affinity group used to co-locate services."""
        return "{0}location".format(self.getServicePrefix())

    def getStorageAccountName(self):
        """Gets the cloud storage account name."""
        return '{0}storage'.format(self.getServicePrefix())

    def getServiceCertificateAlgorithm(self):
        """Gets the algorithm for the service certificate."""
        return self._svc_global['certificate']['algorithm']

    def getServiceCertificateThumbprint(self):
        """Gets the thumbprint for the service certificate."""
        return self._svc_global['certificate']['thumbprint']

    def getServiceCertificateFilename(self):
        """Gets the local path of the file holding the service certificate."""
        return self._svc_global['certificate']['filename']

    def getServiceCertificateKeyFilename(self):
        """Gets the local path of the file holding the service certificate key."""
        return self._svc_global['certificate']['key-filename']

    def getServiceCertificateFormat(self):
        """Gets the format of the service certificate."""
        return self._svc_global['certificate']['format']

    def getServiceCertificatePassword(self):
        """Gets the password for the service certificate."""
        return self._svc_global['certificate']['password']

    def getVirtualMachineLogonUsername(self):
        """Gets the username to log into a virtual machine of the service deployment."""
        return self._svc_global['vm']['username']

    def getVirtualMachineLogonPassword(self):
        """Gets the password to log into a virtual machine of the service deployment."""
        return self._svc_global['vm']['password']

    def getEmailHost(self):
        """Gets the host for the e-mail service."""
        return self._svc_global['e-mail']['host']

    def getEmailUser(self):
        """Gets the username for the e-mail service."""
        return self._svc_global['e-mail']['user']

    def getEmailPassword(self):
        """Gets the password for the e-mail service."""
        return self._svc_global['e-mail']['password']

    def getServiceName(self):
        """Gets the cloud service name."""
        return "{0}{1}".format(self.getServicePrefix(), self.label)

    def getServiceOSImageName(self):
        """Gets the name of the OS image used to create virtual machines in the service deployment."""
        return self._svc['vm']['os-image']

    def getServiceInstanceCount(self):
        """Gets the number of virtual machines to create in the service deployment."""
        return self._svc['vm']['count']

    def getServiceInstanceRoleSize(self):
        """Gets the role size for each virtual machine in the service deployment."""
        return self._svc['vm']['role-size']

    def getServiceInstanceSshPort(self):
        """Gets the base SSH port value. If this value is N, the k-th web instance will have SSH port number (N+k)."""
        return self._svc['vm']['ssh-port']

    def getGitUser(self):
        """Gets the name of the Git user associated with the target source code repository."""
        return self._svc['git']['user']

    def getGitRepo(self):
        """Gets the name of the Git of the target source code repository."""
        return self._svc['git']['repo']

    def getGitTag(self):
        """Gets the Git tag defining the specific version of the source code."""
        return self._svc['git']['tag']

    def getDjangoConfiguration(self):
        """Gets the name of the Django configuration."""
        return self._svc['django']['configuration']

    def getDjangoSecretKey(self):
        """Gets the value of the Django secret key."""
        return self._svc['django']['secret-key']

    def getDatabaseEngine(self):
        """Gets the database engine type."""
        return self._svc['database']['engine']

    def getDatabaseName(self):
        """Gets the database name."""
        return self._svc['database']['name']

    def getDatabaseUser(self):
        """Gets the database username."""
        return self._svc['database']['user']

    def getDatabasePassword(self):
        """Gets the database password."""
        return self._svc['database']['password']

    def getDatabaseHost(self):
        """Gets the database host."""
        return self._svc['database']['host']

    def getDatabasePort(self):
        """Gets the database port."""
        return self._svc['database']['port']

    def getServicePublicStorageContainer(self):
        """Gets the name of the public Blob container for the service."""
        return self._svc['storage']['public-container']

    def getServiceBundleStorageContainer(self):
        """Gets the name of the bundle Blob container for the service."""
        return self._svc['storage']['bundles-container']

    def getServiceBusNamespace(self):
        """Gets the namespace for the service bus."""
        name = self._svc['bus']['namespace']
        if len(name) <= 0:
            cap = DeploymentConfig._cap
            name = '{0}{1}Bus'.format(cap(self.getServicePrefix()), cap(self.label))
        return name

    def getBuildServiceName(self):
        """Gets the cloud service name for the build instance."""
        return "{0}build".format(self.getServicePrefix(), self.label)

    def getBuildOSImageName(self):
        """Gets the name of the OS image used to create the virtual machine for the build server."""
        return self._bld['os-image']

    def getBuildInstanceRoleSize(self):
        """Gets the role size for the build virtual machine."""
        return self._bld['role-size']

    def getBuildHostname(self):
        """
        Gets the name of the build machine. It is of the form '<build-service-name>.cloudapp.net:<port>'.
        """
        return '{0}.cloudapp.net:22'.format(self.getBuildServiceName())

    def getWebHostnames(self):
        """
        Gets the list of web instances. Each name in the list if of the form '<service-name>.cloudapp.net:<port>'.
        """
        service_name = self.getServiceName()
        vm_numbers = range(1, 1 + self.getServiceInstanceCount())
        ssh_port = self.getServiceInstanceSshPort()
        return ['{0}.cloudapp.net:{1}'.format(service_name, str(ssh_port + vm_number)) for vm_number in vm_numbers]

class Deployment(object):
    """
    Helper class to handle deployment of the web site.
    """
    def __init__(self, config):
        self.config = config
        self.sms = ServiceManagementService(config.getAzureSubscriptionId(), config.getAzureCertificatePath())
        self.sbms = ServiceBusManagementService(config.getAzureSubscriptionId(), config.getAzureCertificatePath())

    @staticmethod
    def _resource_exists(get_resource):
        """
        Helper to check for the existence of a resource in Azure.

        get_resource: Parameter-less function to invoke in order to get the resource. The resource
            is assumed to exist when the call to get_resource() returns a value that is not None.
            If the call to get_resource() returns None or throws a WindowsAzureMissingResourceError
            exception, then it is assumed that the resource does not exist.

        Returns: A boolean value which is True if the resource exists.
        """
        resource = None
        try:
            resource = get_resource()
        except WindowsAzureMissingResourceError:
            pass
        return resource is not None

    def _wait_for_operation_success(self, request_id, timeout=600, wait=5):
        """
        Waits for an asynchronous Azure operation to finish.

        request_id: The ID of the request to track.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to fetch the latest operation status.
        """
        result = self.sms.get_operation_status(request_id)
        start_time = time.time()
        max_time = start_time + timeout
        now = start_time
        while result.status == 'InProgress':
            if now >= max_time:
                raise Exception("Operation did not finish within the expected timeout")
            logger.info('Waiting for operation to finish (last_status=%s wait_so_far=%s)',
                        result.status, round(now - start_time, 1))
            time_to_wait = max(0.0, min(max_time - now, wait))
            time.sleep(time_to_wait)
            result = self.sms.get_operation_status(request_id)
            now = time.time()
        if result.status != 'Succeeded':
            raise Exception("Operation terminated but it did not succeed.")

    def _wait_for_role_instance_status(self, role_instance_name, service_name, expected_status, timeout=600, wait=5):
        """
        Waits for a role instance within the web site's cloud service to reach the status specified.

        role_instance_name: Name of the role instance.
        service_name: Name of service in which to find the role instance.
        expected_status: Expected instance status.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to fetch the latest role status.
        """
        start_time = time.time()
        max_time = start_time + timeout
        now = start_time
        while True:
            status = None
            deployment = self.sms.get_deployment_by_name(service_name, service_name)
            for role_instance in deployment.role_instance_list:
                if role_instance.instance_name == role_instance_name:
                    status = role_instance.instance_status
            if status == expected_status:
                break
            if now >= max_time:
                raise Exception("Operation did not finish within the expected timeout")
            logger.info('Waiting for deployment status: expecting %s but got %s (wait_so_far=%s)',
                        expected_status, status, round(now - start_time, 1))
            time_to_wait = max(0.0, min(max_time - now, wait))
            time.sleep(time_to_wait)
            now = time.time()

    def _wait_for_disk_deletion(self, disk_name, timeout=600, wait=5):
        """
        Waits for a VM disk to disappear when it is being deleted.

        disk_name: Name of the VHD.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to check for the existence of the disk.
        """
        start_time = time.time()
        max_time = start_time + timeout
        now = start_time
        logger.info("Checking that disk %s has been deleted.", disk_name)
        while self._resource_exists(lambda: self.sms.get_disk(disk_name)):
            if now >= max_time:
                raise Exception("Disk %s was not deleted within the expected timeout.".format(disk_name))
            logger.info("Waiting for disk %s to disappear (wait_so_far=%s).", disk_name, round(now - start_time, 1))
            time_to_wait = max(0.0, min(max_time - now, wait))
            time.sleep(time_to_wait)
            now = time.time()
        logger.info("Disk %s has been deleted.", disk_name)

    def _wait_for_namespace_active(self, name, timeout=600, wait=5):
        """
        Waits for a service bus namespace to become Active.

        name: Namespace name.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to check for the existence of the disk.
        """
        start_time = time.time()
        max_time = start_time + timeout
        now = start_time
        while True:
            status = None
            props = self.sbms.get_namespace(name)
            status = props.status
            if status == 'Active':
                break
            if now >= max_time:
                raise Exception("Operation did not finish within the expected timeout")
            logger.info('Waiting for namepsace status: expecting Active but got %s (wait_so_far=%s)',
                        status, round(now - start_time, 1))
            time_to_wait = max(0.0, min(max_time - now, wait))
            time.sleep(time_to_wait)
            now = time.time()

    def _getRoleInstances(self, service_name):
        """
        Returns the role instances in the given cloud service deployment. The results are provided as
        a dictionary where keys are role instance names and values are RoleInstance objects.
        """
        role_instances = {}
        if self._resource_exists(lambda: self.sms.get_deployment_by_name(service_name, service_name)):
            deployment = self.sms.get_deployment_by_name(service_name, service_name)
            for role_instance in deployment.role_instance_list:
                role_instances[role_instance.instance_name] = role_instance
        return role_instances

    def _ensureAffinityGroupExists(self):
        """
        Creates the affinity group if it does not exist.
        """
        name = self.config.getAffinityGroupName()
        location = self.config.getServiceLocation()
        logger.info("Checking for existence of affinity group (name=%s; location=%s).", name, location)
        if self._resource_exists(lambda: self.sms.get_affinity_group_properties(name)):
            logger.warn("An affinity group named %s already exists.", name)
        else:
            self.sms.create_affinity_group(name, name, location)
            logger.info("Created affinity group %s.", name)

    def _ensureStorageAccountExists(self):
        """
        Creates the storage account if it does not exist.
        """
        name = self.config.getStorageAccountName()
        logger.info("Checking for existence of storage account (name=%s).", name)
        if self._resource_exists(lambda: self.sms.get_storage_account_properties(name)):
            logger.warn("A storage account named %s already exists.", name)
        else:
            result = self.sms.create_storage_account(name, "", name, affinity_group=self.config.getAffinityGroupName())
            self._wait_for_operation_success(result.request_id, timeout=self.config.getAzureOperationTimeout())
            logger.info("Created storage account %s.", name)

    def _getStorageAccountKey(self, account_name):
        """
        Gets the storage account key (primary key) for the given storage account.
        """
        storage_props = self.sms.get_storage_account_keys(account_name)
        return storage_props.storage_service_keys.primary

    def _ensureStorageContainersExist(self):
        """
        Creates Blob storage containers required by the service.
        """
        logger.info("Checking for existence of Blob containers.")
        account_name = self.config.getStorageAccountName()
        account_key = self._getStorageAccountKey(account_name)
        blob_service = BlobService(account_name, account_key)
        name_and_access_list = [ (self.config.getServicePublicStorageContainer(), 'blob'),
                                 (self.config.getServiceBundleStorageContainer(), None) ]
        for name, access in name_and_access_list:
            logger.info("Checking for existence of Blob container %s.", name)
            blob_service.create_container(name, x_ms_blob_public_access=access, fail_on_exist=False)
            access_info = 'private' if access is None else 'public {0}'.format(access)
            logger.info("Blob container %s is ready (access: %s).", name, access_info)

    def _ensureServiceExists(self, service_name, affinity_group_name):
        """
        Creates the specified cloud service host if it does not exist.

        service_name: Name of the cloud service.
        affinity_group_name: Name of the affinity group (which should exists).
        """
        logger.info("Checking for existence of cloud service (name=%s).", service_name)
        if self._resource_exists(lambda: self.sms.get_hosted_service_properties(service_name)):
            logger.warn("A cloud service named %s already exists.", service_name)
        else:
            self.sms.create_hosted_service(service_name, service_name, affinity_group=affinity_group_name)
            logger.info("Created cloud service %s.", service_name)

    def _ensureServiceCertificateExists(self, service_name):
        """
        Adds certificate to the specified cloud service.

        service_name: Name of the target cloud service (which should exist).
        """
        cert_format = self.config.getServiceCertificateFormat()
        cert_algorithm = self.config.getServiceCertificateAlgorithm()
        cert_thumbprint = self.config.getServiceCertificateThumbprint()
        cert_path = self.config.getServiceCertificateFilename()
        cert_password = self.config.getServiceCertificatePassword()
        logger.info("Checking for existence of cloud service certificate for service %s.", service_name)
        get_cert = lambda: self.sms.get_service_certificate(service_name, cert_algorithm, cert_thumbprint)
        if self._resource_exists(get_cert):
            logger.info("Found expected cloud service certificate.")
        else:
            with open(cert_path, 'rb') as f:
                cert_data = base64.b64encode(f.read())
            if len(cert_data) <= 0:
                raise Exception("Detected invalid certificate data.")
            result = self.sms.add_service_certificate(service_name, cert_data, cert_format, cert_password)
            self._wait_for_operation_success(result.request_id, timeout=self.config.getAzureOperationTimeout())
            logger.info("Added service certificate.")

    def _assertOsImageExists(self, os_image_name):
        """
        Asserts that the named OS image exists.
        """
        logger.info("Checking for availability of OS image (name=%s).", os_image_name)
        if self.sms.get_os_image(os_image_name) is None:
            raise Exception("Unable to find OS Image '{0}'.".format(os_image_name))

    def _ensureVirtualMachinesExist(self):
        """
        Creates the VMs for the web site.
        """
        service_name = self.config.getServiceName()
        cert_thumbprint = self.config.getServiceCertificateThumbprint()
        vm_username = self.config.getVirtualMachineLogonUsername()
        vm_password = self.config.getVirtualMachineLogonPassword()
        vm_role_size = self.config.getServiceInstanceRoleSize()
        vm_numbers = self.config.getServiceInstanceCount()
        if vm_numbers < 1:
            raise Exception("Detected an invalid number of instances: {0}.".format(vm_numbers))

        self._assertOsImageExists(self.config.getServiceOSImageName())

        role_instances = self._getRoleInstances(service_name)
        for vm_number in range(1, vm_numbers+1):
            vm_hostname = '{0}-{1}'.format(service_name, vm_number)
            if vm_hostname in role_instances:
                logger.warn("Role instance %s already exists: skipping creation.", vm_hostname)
                continue

            logger.info("Role instance %s provisioning begins.", vm_hostname)
            vm_diskname = '{0}.vhd'.format(vm_hostname)
            vm_disk_media_link = 'http://{0}.blob.core.windows.net/vhds/{1}'.format(
                self.config.getStorageAccountName(), vm_diskname
            )
            ssh_port = str(self.config.getServiceInstanceSshPort() + vm_number)

            os_hd = OSVirtualHardDisk(self.config.getServiceOSImageName(),
                                      vm_disk_media_link,
                                      disk_name = vm_diskname,
                                      disk_label = vm_diskname)
            linux_config = LinuxConfigurationSet(vm_hostname, vm_username, vm_password, True)
            linux_config.ssh.public_keys.public_keys.append(
                PublicKey(cert_thumbprint, u'/home/{0}/.ssh/authorized_keys'.format(vm_username))
            )
            linux_config.ssh.key_pairs.key_pairs.append(
                KeyPair(cert_thumbprint, u'/home/{0}/.ssh/id_rsa'.format(vm_username))
            )
            network_config = ConfigurationSet()
            network_config.configuration_set_type = 'NetworkConfiguration'
            ssh_endpoint = ConfigurationSetInputEndpoint(name='SSH',
                                                         protocol='TCP',
                                                         port=ssh_port,
                                                         local_port=u'22')
            network_config.input_endpoints.input_endpoints.append(ssh_endpoint)
            http_endpoint = ConfigurationSetInputEndpoint(name='HTTP',
                                                          protocol='TCP',
                                                          port=u'80',
                                                          local_port=u'80',
                                                          load_balanced_endpoint_set_name=service_name)
            http_endpoint.load_balancer_probe.port = '80'
            http_endpoint.load_balancer_probe.protocol = 'TCP'
            network_config.input_endpoints.input_endpoints.append(http_endpoint)

            if (vm_number == 1):
                result = self.sms.create_virtual_machine_deployment(service_name=service_name,
                                                                    deployment_name=service_name,
                                                                    deployment_slot='Production',
                                                                    label=vm_hostname,
                                                                    role_name=vm_hostname,
                                                                    system_config=linux_config,
                                                                    os_virtual_hard_disk=os_hd,
                                                                    network_config=network_config,
                                                                    availability_set_name=service_name,
                                                                    data_virtual_hard_disks=None,
                                                                    role_size=vm_role_size)
                self._wait_for_operation_success(result.request_id,
                                                 timeout=self.config.getAzureOperationTimeout())
                self._wait_for_role_instance_status(vm_hostname, service_name, 'ReadyRole',
                                                    self.config.getAzureOperationTimeout())
            else:
                result = self.sms.add_role(service_name=service_name,
                                           deployment_name=service_name,
                                           role_name=vm_hostname,
                                           system_config=linux_config,
                                           os_virtual_hard_disk=os_hd,
                                           network_config=network_config,
                                           availability_set_name=service_name,
                                           role_size=vm_role_size)
                self._wait_for_operation_success(result.request_id,
                                                 timeout=self.config.getAzureOperationTimeout())
                self._wait_for_role_instance_status(vm_hostname, service_name, 'ReadyRole',
                                                    self.config.getAzureOperationTimeout())

            logger.info("Role instance %s has been created.", vm_hostname)

    def _deleteVirtualMachines(self, service_name):
        """
        Deletes the VMs in the given cloud service.
        """
        if self._resource_exists(lambda: self.sms.get_deployment_by_name(service_name, service_name)) == False:
            logger.warn("Deployment %s not found: no VMs to delete.", service_name)
        else:
            logger.info("Attempting to delete deployment %s.", service_name)
            # Get set of role instances before we remove them
            role_instances = self._getRoleInstances(service_name)

            def update_request(request):
                """
                A filter to intercept the HTTP request sent by the ServiceManagementService
                so we can take advantage of a newer feature ('comp=media') in the delete deployment API
                (see http://msdn.microsoft.com/en-us/library/windowsazure/ee460812.aspx)
                """
                hdrs = []
                for name, value in request.headers:
                    if 'x-ms-version' == name:
                        value = '2013-08-01'
                    hdrs.append((name, value))
                request.headers = hdrs
                request.path = request.path + '?comp=media'
                #pylint: disable=W0212
                response = self.sms._filter(request)
                return response

            svc = ServiceManagementService(self.sms.subscription_id, self.sms.cert_file)
            #pylint: disable=W0212
            svc._filter = update_request
            result = svc.delete_deployment(service_name, service_name)
            logger.info("Deployment %s deletion in progress: waiting for delete_deployment operation.", service_name)
            self._wait_for_operation_success(result.request_id)
            logger.info("Deployment %s deletion in progress: waiting for VM disks to be removed.", service_name)
            # Now wait for the disks to disappear
            for role_instance_name in role_instances.keys():
                disk_name = "{0}.vhd".format(role_instance_name)
                self._wait_for_disk_deletion(disk_name)
            logger.info("Deployment %s deleted.", service_name)

    def _ensureBuildMachineExists(self):
        """
        Creates the VM for the build server.
        """
        service_name = self.config.getBuildServiceName()
        service_storage_name = self.config.getStorageAccountName()
        cert_thumbprint = self.config.getServiceCertificateThumbprint()
        vm_username = self.config.getVirtualMachineLogonUsername()
        vm_password = self.config.getVirtualMachineLogonPassword()
        vm_hostname = service_name

        role_instances = self._getRoleInstances(service_name)
        if vm_hostname in role_instances:
            logger.warn("Role instance %s already exists: skipping creation.", vm_hostname)
        else:
            logger.info("Role instance %s provisioning begins.", vm_hostname)
            self._assertOsImageExists(self.config.getBuildOSImageName())

            vm_diskname = '{0}.vhd'.format(vm_hostname)
            vm_disk_media_link = 'http://{0}.blob.core.windows.net/vhds/{1}'.format(service_storage_name, vm_diskname)
            os_hd = OSVirtualHardDisk(self.config.getBuildOSImageName(),
                                      vm_disk_media_link,
                                      disk_name = vm_diskname,
                                      disk_label = vm_diskname)
            linux_config = LinuxConfigurationSet(vm_hostname, vm_username, vm_password, True)
            linux_config.ssh.public_keys.public_keys.append(
                PublicKey(cert_thumbprint, u'/home/{0}/.ssh/authorized_keys'.format(vm_username))
            )
            linux_config.ssh.key_pairs.key_pairs.append(
                KeyPair(cert_thumbprint, u'/home/{0}/.ssh/id_rsa'.format(vm_username))
            )
            network_config = ConfigurationSet()
            network_config.configuration_set_type = 'NetworkConfiguration'
            ssh_endpoint = ConfigurationSetInputEndpoint(name='SSH',
                                                         protocol='TCP',
                                                         port=u'22',
                                                         local_port=u'22')
            network_config.input_endpoints.input_endpoints.append(ssh_endpoint)

            result = self.sms.create_virtual_machine_deployment(service_name=service_name,
                                                                deployment_name=service_name,
                                                                deployment_slot='Production',
                                                                label=vm_hostname,
                                                                role_name=vm_hostname,
                                                                system_config=linux_config,
                                                                os_virtual_hard_disk=os_hd,
                                                                network_config=network_config,
                                                                availability_set_name=None,
                                                                data_virtual_hard_disks=None,
                                                                role_size=self.config.getBuildInstanceRoleSize())
            self._wait_for_operation_success(result.request_id, timeout = self.config.getAzureOperationTimeout())
            self._wait_for_role_instance_status(vm_hostname, service_name, 'ReadyRole',
                                                self.config.getAzureOperationTimeout())
            logger.info("Role instance %s has been created.", vm_hostname)

    def _deleteStorageAccount(self):
        """
        Deletes the storage account for the web site.
        """
        name = self.config.getStorageAccountName()
        logger.info("Attempting to delete storage account %s.", name)
        if self._resource_exists(lambda: self.sms.get_storage_account_properties(name)) == False:
            logger.warn("Storage account %s not found: nothing to delete.", name)
        else:
            self.sms.delete_storage_account(name)
            logger.info("Storage account %s deleted.", name)

    def _deleteService(self, name):
        """
        Deletes the specified cloud service.
        """
        logger.info("Attempting to delete cloud service %s.", name)
        if self._resource_exists(lambda: self.sms.get_hosted_service_properties(name)) == False:
            logger.warn("Cloud service %s not found: nothing to delete.", name)
        else:
            self.sms.delete_hosted_service(name)
            logger.info("Cloud service %s deleted.", name)

    def _deleteAffinityGroup(self):
        """
        Deletes the affinity group for the web site.
        """
        name = self.config.getAffinityGroupName()
        logger.info("Attempting to delete affinity group %s.", name)
        if self._resource_exists(lambda: self.sms.get_affinity_group_properties(name)) == False:
            logger.warn("Affinity group %s not found: nothing to delete.", name)
        else:
            self.sms.delete_affinity_group(name)
            logger.info("Affinity group %s deleted.", name)

    def _ensureServiceBusNamespaceExists(self):
        """
        Creates the Azure Service Bus Namespace if it does not exist.
        """
        name = self.config.getServiceBusNamespace()
        logger.info("Checking for existence of service bus namespace (name=%s).", name)
        if self._resource_exists(lambda: self.sbms.get_namespace(name)):
            logger.warn("A namespace named %s already exists.", name)
        else:
            self.sbms.create_namespace(name, self.config.getServiceLocation())
            self._wait_for_namespace_active(name)
            logger.info("Created namespace %s.", name)

    def _ensureServiceBusQueuesExist(self):
        """
        Creates Azure service bus queues required by the service.
        """
        logger.info("Checking for existence of Service Bus Queues.")
        namespace = self.sbms.get_namespace(self.config.getServiceBusNamespace())
        sbs = ServiceBusService(namespace.name, namespace.default_key, issuer='owner')
        queue_names = [ 'jobresponsequeue', 'windowscomputequeue', 'linuxcomputequeue' ]
        for name in queue_names:
            logger.info("Checking for existence of Queue %s.", name)
            sbs.create_queue(name, fail_on_exist=False)
            logger.info("Queue %s is ready.", name)

    def _deleteServiceBusNamespace(self):
        """
        Deletes the Azure Service Bus Namespace.
        """
        name = self.config.getServiceBusNamespace()
        logger.info("Attempting to delete service bus namespace %s.", name)
        if self._resource_exists(lambda: self.sbms.get_namespace(name)) == False:
            logger.warn("Namespace %s not found: nothing to delete.", name)
        else:
            self.sbms.delete_namespace(name)
            logger.info("Namespace %s deleted.", name)

    def Deploy(self, assets):
        """
        Creates a deployment.

        assets: The set of assets to create. The full set is: {'build', 'web'}.
        """
        if len(assets) == 0:
            raise ValueError("Set of assets to deploy is not specified.")
        logger.info("Starting deployment operation.")
        self._ensureAffinityGroupExists()
        self._ensureStorageAccountExists()
        ## Build instance
        if 'build' in assets:
            self._ensureServiceExists(self.config.getBuildServiceName(), self.config.getAffinityGroupName())
            self._ensureServiceCertificateExists(self.config.getBuildServiceName())
            self._ensureBuildMachineExists()
        # Web instances
        if 'web' in assets:
            self._ensureStorageContainersExist()
            self._ensureServiceBusNamespaceExists()
            self._ensureServiceBusQueuesExist()
            self._ensureServiceExists(self.config.getServiceName(), self.config.getAffinityGroupName())
            self._ensureServiceCertificateExists(self.config.getServiceName())
            self._ensureVirtualMachinesExist()
        #queues
        logger.info("Deployment operation is complete.")

    def Teardown(self, assets):
        """
        Deletes a deployment.

        assets: The set of assets to delete. The full set is: {'web', 'build'}.
        """
        if len(assets) == 0:
            raise ValueError("Set of assets to teardown is not specified.")
        logger.info("Starting teardown operation.")
        if 'web' in assets:
            self._deleteVirtualMachines(self.config.getServiceName())
            self._deleteService(self.config.getServiceName())
        if 'build' in assets:
            self._deleteVirtualMachines(self.config.getBuildServiceName())
            self._deleteService(self.config.getBuildServiceName())
        if ('web' in assets) and ('build' in assets):
            self._deleteServiceBusNamespace()
            self._deleteStorageAccount()
            self._deleteAffinityGroup()
        logger.info("Teardown operation is complete.")

    def getSettingsFileContent(self):
        """
        Generates the content of the local Django settings file.
        """
        allowed_hosts = ['{0}.cloudapp.net'.format(self.config.getServiceName())]
        allowed_hosts.extend(self.config.getWebHostnames())
        allowed_hosts.extend(['www.codalab.org','codalab.org'])

        storage_key = self._getStorageAccountKey(self.config.getStorageAccountName())
        namespace = self.sbms.get_namespace(self.config.getServiceBusNamespace())

        lines = [
            "from base import Base",
            "from default import *",
            "from configurations import Settings",
            "",
            "class {0}(Base):".format(self.config.getDjangoConfiguration()),
            "",
            "    DEBUG=False",
            "",
            "    ALLOWED_HOSTS = {0}".format(allowed_hosts),
            "",
            "    DEFAULT_FILE_STORAGE = 'codalab.azure_storage.AzureStorage'",
            "    AZURE_ACCOUNT_NAME = '{0}'".format(self.config.getStorageAccountName()),
            "    AZURE_ACCOUNT_KEY = '{0}'".format(storage_key),
            "    AZURE_CONTAINER = '{0}'".format(self.config.getServicePublicStorageContainer()),
            "    BUNDLE_AZURE_ACCOUNT_NAME = AZURE_ACCOUNT_NAME",
            "    BUNDLE_AZURE_ACCOUNT_KEY = AZURE_ACCOUNT_KEY",
            "    BUNDLE_AZURE_CONTAINER = '{0}'".format(self.config.getServiceBundleStorageContainer()),
            "",
            "    SBS_NAMESPACE = '{0}'".format(self.config.getServiceBusNamespace()),
            "    SBS_ISSUER = 'owner'",
            "    SBS_ACCOUNT_KEY = '{0}'".format(namespace.default_key),
            "    SBS_RESPONSE_QUEUE = 'jobresponsequeue'",
            "    SBS_COMPUTE_QUEUE = 'windowscomputequeue'",
            "",
            "    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'",
            "    EMAIL_HOST = '{0}'".format(self.config.getEmailHost()),
            "    EMAIL_HOST_USER = '{0}'".format(self.config.getEmailUser()),
            "    EMAIL_HOST_PASSWORD = '{0}'".format(self.config.getEmailPassword()),
            "    EMAIL_PORT = 587",
            "    EMAIL_USE_TLS = True",
            "    DEFAULT_FROM_EMAIL = 'info@codalab.org'",
            "    SERVER_EMAIL = 'info@codalab.org'",
            "",
            "    # Django secret",
            "    SECRET_KEY = '{0}'".format(self.config.getDjangoSecretKey()),
            "",
            "    ADMINS = (('CodaLab', 'codalab@live.com'),)",
            "    MANAGERS = ADMINS",
            "",
            "    DATABASES = {",
            "        'default': {",
            "            'ENGINE': '{0}',".format(self.config.getDatabaseEngine()),
            "            'NAME': '{0}',".format(self.config.getDatabaseName()),
            "            'USER': '{0}',".format(self.config.getDatabaseUser()),
            "            'PASSWORD': '{0}',".format(self.config.getDatabasePassword()),
            "            'HOST': '{0}',".format(self.config.getDatabaseHost()),
            "            'PORT': '{0}', ".format(self.config.getDatabasePort()),
            "        }",
            "    }",
        ]
        return '\n'.join(lines)


if __name__ == "__main__":

    configuration = DeploymentConfig('dev', r'c:\cygwin64\home\cpoulain\.devconfig')
    logging.config.dictConfig(configuration.getLoggerDictConfig())
    logger.info("Loaded configuration from file: %s", configuration.getFilename())
    assets_to_deploy = {} # {'build', 'web'}
    assets_to_teardown = {} # {'web', 'build', 'rest'}
    try:
        dep = Deployment(configuration)
        if len(assets_to_deploy) > 0:
            dep.Deploy(assets_to_deploy)
        if len(assets_to_teardown) > 0:
            dep.Teardown(assets_to_teardown)
    except Exception:
        logger.exception("An unexpected error occurred.")

