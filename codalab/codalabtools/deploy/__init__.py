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
                                     ServiceManagementService)

from codalabtools import BaseConfig

logger = logging.getLogger('codalabtools')

class DeploymentConfig(BaseConfig):
    """
    Defines credentials and configuration values needed to deploy CodaLab.
    """
    def __init__(self, filename='.codalabconfig'):
        super(DeploymentConfig, self).__init__(filename)
        self._dinfo = self.info['deployment']

    def getLoggerDictConfig(self):
        """Gets Dict config for logging configuration."""
        if 'logging' in self._dinfo:
            return self._dinfo['logging']
        else:
            return super(DeploymentConfig, self).getLoggerDictConfig()

    def getAzureSubscriptionId(self):
        """Gets the Azure Subscription ID."""
        return self._dinfo['azure']['subscription-id']

    def getAzureCertificatePath(self):
        """Gets the path for the Azure Service Management certificate."""
        return self._dinfo['azure']['certificate-path']

    def getAzureOperationShortTimeout(self):
        """
        Gets a duration (in seconds) to limit the time spent waiting for the completion
        of a long running operation in Azure.
        """
        return self._dinfo['azure']['operation-timeout-short']

    def getAzureOperationLongTimeout(self):
        """
        Gets a duration (in seconds) to limit the time spent waiting for the completion
        of a long running operation in Azure.
        """
        return self._dinfo['azure']['operation-timeout-long']

    def getServiceName(self):
        """Gets the cloud service name."""
        return self._dinfo['service']['name']

    def getServiceLocation(self):
        """Gets the name of the Azure region in which services will be deployed."""
        return self._dinfo['service']['location']

    def getAffinityGroupName(self):
        """Gets the name of the affinity group used to co-locate services."""
        return "{0}-location".format(self.getServiceName())

    def getStorageAccountName(self):
        """Gets the cloud storage account name."""
        if 'storage-account' in self._dinfo:
            return self._dinfo['storage-account']
        return self.getServiceName()

    def getServiceCertificateAlgorithm(self):
        """Gets the algorithm for the service certificate."""
        return self._dinfo['service']['certificate']['algorithm']

    def getServiceCertificateThumbprint(self):
        """Gets the thumbprint for the service certificate."""
        return self._dinfo['service']['certificate']['thumbprint']

    def getServiceCertificateLocalPath(self):
        """Gets the local path of the file holding the service certificate."""
        return self._dinfo['service']['certificate']['local-path']

    def getServiceCertificateFormat(self):
        """Gets the format of the service certificate."""
        return self._dinfo['service']['certificate']['format']

    def getServiceCertificatePassword(self):
        """Gets the password for the service certificate."""
        return self._dinfo['service']['certificate']['password']

    def getServiceOSImageName(self):
        """Gets the name of the OS image used to create virtual machines in the service deployment."""
        return self._dinfo['service']['os-image']

    def getServiceInstanceCount(self):
        """Gets the number of virtual machines to create in the service deployment."""
        return self._dinfo['service']['vm-count']

    def getServiceInstanceRoleSize(self):
        """Gets the role size for each virtual machine in the service deployment."""
        return self._dinfo['service']['vm-role-size']

    def getServiceInstanceLogonUsername(self):
        """Gets the username to log into a virtual machine of the service deployment."""
        return self._dinfo['service']['vm-username']

    def getServiceInstanceLogonPassword(self):
        """Gets the password to log into a virtual machine of the service deployment."""
        return self._dinfo['service']['vm-password']


class Deployment(object):
    """
    Helper class to handle deployment of the web site.
    """
    def __init__(self, config):
        self.config = config
        self.sms = ServiceManagementService(config.getAzureSubscriptionId(), config.getAzureCertificatePath())

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
        wait_so_far = 0
        result = self.sms.get_operation_status(request_id)
        while result.status == 'InProgress':
            if wait_so_far > timeout:
                raise Exception("Operation did not finish within the expected timeout")
            logger.info('Waiting for operation to finish (last_status=%s wait_so_far=%s)', result.status, wait_so_far)
            time_to_wait = max(0.0, min(timeout - wait_so_far, wait))
            time.sleep(time_to_wait)
            wait_so_far += time_to_wait
            result = self.sms.get_operation_status(request_id)
        if result.status != 'Succeeded':
            raise Exception("Operation terminated but it did not succeed.")

    def _wait_for_role_instance_status(self, role_instance_name, expected_status, timeout=300, wait=5):
        """
        Waits for a role instance within the web site's cloud service to reach the status specified.

        role_instance_name: Name of the role instance.
        expected_status: Expected instance status.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to fetch the latest role status.
        """
        wait_so_far = 0
        service_name = self.config.getServiceName()
        while True:
            status = None
            deployment = self.sms.get_deployment_by_name(service_name, service_name)
            for role_instance in deployment.role_instance_list:
                if role_instance.instance_name == role_instance_name:
                    status = role_instance.instance_status
            if status == expected_status:
                break
            if wait_so_far > timeout:
                raise Exception("Operation did not finish within the expected timeout")
            logger.info('Waiting for deployment status: expecting %s but got %s (wait_so_far=%s)',
                        expected_status, status, wait_so_far)
            time_to_wait = max(0.0, min(timeout - wait_so_far, wait))
            time.sleep(time_to_wait)
            wait_so_far += time_to_wait

    def _wait_for_disk_deletion(self, disk_name, timeout=600, wait=5):
        """
        Waits for a VM disk to disappear when it is being deleted.

        disk_name: Name of the VHD.
        timeout: Maximum duration (in seconds) allowed for the operation to complete.
        wait: Wait time (in seconds) between consecutive calls to check for the existence of the disk.
        """
        wait_so_far = 0
        logger.info("Checking that disk %s has been deleted.", disk_name)
        while self._resource_exists(lambda: self.sms.get_disk(disk_name)):
            if wait_so_far > timeout:
                raise Exception("Disk %s was not deleted within the expected timeout.".format(disk_name))
            logger.info("Waiting for disk %s to disappear (wait_so_far=%s).", disk_name, wait_so_far)
            time_to_wait = max(0.0, min(timeout - wait_so_far, wait))
            time.sleep(time_to_wait)
            wait_so_far += time_to_wait
        logger.info("Disk %s has been deleted.", disk_name)

    def _getRoleInstances(self):
        """
        Returns the role instances in the web site deployment as a dictionary keyed by the name of
        the role instance. Values are RoleInstance objects.
        """
        role_instances = {}
        service_name = self.config.getServiceName()
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
            self._wait_for_operation_success(result.request_id, timeout=self.config.getAzureOperationShortTimeout())
            logger.info("Created storage account %s.", name)

    def _ensureServiceExists(self):
        """
        Creates the cloud service host if it does not exist.
        """
        name = self.config.getServiceName()
        logger.info("Checking for existence of cloud service (name=%s).", name)
        if self._resource_exists(lambda: self.sms.get_hosted_service_properties(name)):
            logger.warn("A cloud service named %s already exists.", name)
        else:
            self.sms.create_hosted_service(name, name, affinity_group=self.config.getAffinityGroupName())
            logger.info("Created cloud service %s.", name)

    def _ensureServiceCertificateExists(self):
        """
        Adds certificate to the cloud service.
        """
        service_name = self.config.getServiceName()
        cert_format = self.config.getServiceCertificateFormat()
        cert_algorithm = self.config.getServiceCertificateAlgorithm()
        cert_thumbprint = self.config.getServiceCertificateThumbprint()
        cert_path = self.config.getServiceCertificateLocalPath()
        cert_password = self.config.getServiceCertificatePassword()
        logger.info("Checking for existence of cloud service certificate.")
        get_cert = lambda: self.sms.get_service_certificate(service_name, cert_algorithm, cert_thumbprint)
        if self._resource_exists(get_cert):
            logger.info("Found expected cloud service certificate.")
        else:
            with open(cert_path, 'rb') as f:
                cert_data = base64.b64encode(f.read())
            if len(cert_data) <= 0:
                raise Exception("Detected invalid certificate data.")
            result = self.sms.add_service_certificate(service_name, cert_data, cert_format, cert_password)
            self._wait_for_operation_success(result.request_id, timeout=self.config.getAzureOperationShortTimeout())
            logger.info("Added service certificate.")

    def _ensureVirtualMachinesExist(self):
        """
        Creates the VMs for the web site.
        """
        service_name = self.config.getServiceName()
        service_storage_name = self.config.getStorageAccountName()
        cert_thumbprint = self.config.getServiceCertificateThumbprint()
        short_timeout = self.config.getAzureOperationShortTimeout()
        long_timeout = self.config.getAzureOperationLongTimeout()
        vm_username = self.config.getServiceInstanceLogonUsername()
        vm_password = self.config.getServiceInstanceLogonPassword()
        vm_role_size = self.config.getServiceInstanceRoleSize()
        vm_numbers = self.config.getServiceInstanceCount()
        if vm_numbers < 1:
            raise Exception("Detected an invalid number of instances: {0}.".format(vm_numbers))

        os_image_name = self.config.getServiceOSImageName()
        logger.info("Checking for availability of OS image (name=%s).", os_image_name)
        if self.sms.get_os_image(os_image_name) is None:
            raise Exception("Unable to find OS Image '{0}'.".format(os_image_name))

        role_instances = self._getRoleInstances()
        for vm_number in range(1, vm_numbers+1):
            vm_hostname = '{0}-{1}'.format(service_name, vm_number)
            if vm_hostname in role_instances:
                logger.warn("Role instance %s already exists: skipping creation.", vm_hostname)
                continue

            logger.info("Role instance %s provisioning begins.", vm_hostname)
            vm_diskname = '{0}.vhd'.format(vm_hostname)
            vm_disk_media_link = 'http://{0}.blob.core.windows.net/vhds/{1}'.format(service_storage_name, vm_diskname)
            ssh_port = str(57190 + vm_number)

            os_hd = OSVirtualHardDisk(os_image_name,
                                      vm_disk_media_link,
                                      disk_name = vm_diskname,
                                      disk_label = vm_diskname)
            linux_config = LinuxConfigurationSet(vm_hostname, vm_username, vm_password, False) #disable password auth?
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
                self._wait_for_operation_success(result.request_id, timeout = short_timeout)
                self._wait_for_role_instance_status(vm_hostname, 'ReadyRole', long_timeout)
            else:
                result = self.sms.add_role(service_name=service_name,
                                           deployment_name=service_name,
                                           role_name=vm_hostname,
                                           system_config=linux_config,
                                           os_virtual_hard_disk=os_hd,
                                           network_config=network_config,
                                           availability_set_name=service_name,
                                           role_size=vm_role_size)
                self._wait_for_operation_success(result.request_id, timeout = short_timeout)
                self._wait_for_role_instance_status(vm_hostname, 'ReadyRole', long_timeout)

            logger.info("Role instance %s has been created.", vm_hostname)

    def _deleteVirtualMachines(self):
        """
        Deletes the VMs for the web site.
        """
        service_name = self.config.getServiceName()
        if self._resource_exists(lambda: self.sms.get_deployment_by_name(service_name, service_name)) == False:
            logger.warn("Deployment %s not found: no VMs to delete.", service_name)
        else:
            logger.info("Attempting to delete deployment %s.", service_name)
            # Get set of role instances before we remove them
            role_instances = self._getRoleInstances()

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

    def _deleteService(self):
        """
        Deletes the cloud service for the web site.
        """
        name = self.config.getServiceName()
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

    def Deploy(self):
        """
        Creates a deployment.
        """
        logger.info("Starting deployment operation.")
        self._ensureAffinityGroupExists()
        self._ensureStorageAccountExists()
        self._ensureServiceExists()
        self._ensureServiceCertificateExists()
        self._ensureVirtualMachinesExist()
        logger.info("Deployment operation is complete.")
        #queues

    def Teardown(self):
        """
        Deletes a deployment.
        """
        logger.info("Starting teardown operation.")
        self._deleteVirtualMachines()
        self._deleteService()
        self._deleteStorageAccount()
        self._deleteAffinityGroup()
        logger.info("Teardown operation is complete.")

if __name__ == "__main__":
    configuration = DeploymentConfig(r'..\..\.codalabconfig')
    logging.config.dictConfig(configuration.getLoggerDictConfig())
    logger.info("Loaded configuration from file: %s", configuration.getFilename())
    try:
        dep = Deployment(configuration)
        dep.Deploy()
        #dep.Teardown()
    except Exception:
        logger.exception("An unexpected error occurred.")

