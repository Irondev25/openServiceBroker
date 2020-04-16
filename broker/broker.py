import logging

from openbrokerapi import api
from openbrokerapi.service_broker import (
    ServiceBroker,
    UnbindDetails,
    BindDetails,
    Binding,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    ProvisionDetails,
    ProvisionedServiceSpec,
    Service,
    UnbindSpec,
    ProvisionState)
from openbrokerapi.catalog import ServicePlan
from openbrokerapi import errors
from broker import jenkins_utils

logger = logging.getLogger(__name__)


class Broker(ServiceBroker):
    """
    This class should be implemented.

    The minimum setup to register a service broker requires the `catalog()`.
    To create and delete a service instance `provision` and `deprovision` are required.
    To bind and unbind a service instance you have to implement `bind` and `unbind` in addition.

    If some steps are async, you will have to add further methods. Please have a look in the Open Service Broker Spec.
    """
    CREATING = 'CREATING'
    CREATED = 'CREATED'
    BINDING = 'BINDING'
    BOUND = 'BOUND'
    UNBINDING = 'UNBINDING'
    DELETING = 'DELETING'

    def __init__(self,service_guid,plan_guid):
        self.service_guid = service_guid
        self.plan_guid = plan_guid
        self.service_instances = dict()

    def catalog(self) -> Service:
        return Service(
            id=self.service_guid,
            name='Jenkins enabled Git',
            description='Create jenkins job for a given git repo',
            bindable=False,
            plans=[
                ServicePlan(
                    id=self.plan_guid,
                    name='Testing Plan',
                    description='Used in Testing process',
                    free=True
                )
            ]
        )

    def provision(self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs) -> ProvisionedServiceSpec:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        if instance_id in self.service_instances.keys():
            raise errors.ErrInstanceAlreadyExists()
        self.service_instances[instance_id] = {
            'provision_details':details,
            'state': self.CREATING
        }
        try:
            github_url = details.parameters.get('git_repo_url')
            github_id = details.parameters.get('github_id')
            github_pass = details.parameters.get('github_pass')
            provision_details = jenkins_utils.provision_job(github_url, github_id, github_pass)
            # jenkins_utils.provision_job(githib_url)
        except Exception as e:
            print(e)
            raise errors.ServiceException()
        self.service_instances[instance_id] = {
            'provision_details': details,
            'state': self.CREATED,
            'job_name': provision_details['job_name'],
            'github_hook_id': provision_details['github_hook_id'],
            'github_api_url': provision_details['github_api_url']
        }
        return ProvisionedServiceSpec(
            state=ProvisionState.IS_ASYNC,
            operation='provision'
        )

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool, **kwargs) -> DeprovisionServiceSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()
        if instance.get('state') == self.CREATED:
            print(self.service_instances[instance_id])
            context_instance = self.service_instances[instance_id]
            job_name = context_instance['job_name']
            github_hook_id = context_instance['github_hook_id']
            github_api_url = context_instance['github_api_url']
            jenkins_utils.deprovision_job(job_name, github_hook_id, github_api_url)
            del self.service_instances[instance_id]
            return DeprovisionServiceSpec(False)

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        pass

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool, **kwargs) -> UnbindSpec:
        pass


def create_broker_blueprint(credentials: api.BrokerCredentials):
    return api.get_blueprint(Broker("Jenkins-Broker","Jenkins-Plan-GID"), credentials, logger)
