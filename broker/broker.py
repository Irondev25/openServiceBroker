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
    ProvisionState,
    BindState, 
    GetInstanceDetailsSpec,
    GetBindingSpec)
from openbrokerapi.catalog import ServicePlan
from openbrokerapi import errors
from broker import jenkins_utils
from broker import github_utils

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
            bindable=True,
            bindings_retrievable=True,
            instances_retrievable=True,
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
            project_name = details.parameters.get('project_name')
            github_id = details.parameters.get('github_id')
            github_pass = details.parameters.get('github_pass')
            email_id = details.parameters.get('email')
            repo_details = jenkins_utils.provision_job(project_name, github_id, github_pass, email_id)
            # jenkins_utils.provision_job(githib_url)
        except Exception as e:
            print(e)
            raise errors.ServiceException(e)

        # repo_details = {
        #     'html_url' : repo.html_url,
        #     'clone_url': repo.clone_url,
        #     'hooks_url': repo.hooks_url,
        #     'hook_id'  : hook.id
        # }
        
        self.service_instances[instance_id] = {
            'provision_details': details,
            'state': self.CREATED,
            'project_name': project_name,
            'repo_html_url': repo_details.get('html_url'),
            'repo_clone_url': repo_details.get('clone_url'),
            'repo_hooks_url': repo_details.get('hooks_url'),
            'repo_hook_id': repo_details.get('hook_id')
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
            project_name = context_instance.get('project_name')
            api_url = context_instance.get('repo_hooks_url') #api endpoint to delete hook
            hook_id = context_instance.get('repo_hook_id') #hook id
            jenkins_utils.deprovision_job(project_name, api_url, hook_id)
            del self.service_instances[instance_id]
            return DeprovisionServiceSpec(False)
        elif instance.get('state') in [self.BOUND,self.BINDING]:
            raise errors.ErrBadRequest("Instance Binded,Can't deprovision")

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        instance = self.service_instances.get(instance_id,{})
        if instance and instance.get('state') == self.CREATED:
            self.service_instances[instance_id]['state'] = self.BINDING
            clone_url = instance.get('repo_clone_url')
            html_url = instance.get('repo_html_url')
            credentials = {
                'git_repo_url': html_url,
                'git_repo_clone_url': clone_url
            }
            self.service_instances[instance_id]['state'] = self.BOUND
            return Binding(state=BindState.SUCCESSFUL_BOUND,credentials=credentials)
        else:
            raise errors.ErrBindingAlreadyExists()

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool, **kwargs) -> UnbindSpec:
        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get('state') == self.BOUND:
            self.service_instances[instance_id]['state'] = self.UNBINDING
            self.service_instances[instance_id]['state'] = self.CREATED
            return UnbindSpec(False)

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()
        provision_detail = instance.get('provision_details')
        parameters = {
            'github_repo': instance.get('repo_clone_url') 
        }
        return GetInstanceDetailsSpec(provision_detail.service_id,provision_detail.plan_id,parameters=parameters)
    
    def get_binding(self,
                    instance_id: str,
                    binding_id: str,
                    **kwargs
                    ) -> GetBindingSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()
        if instance.get('state') == self.BOUND:
            clone_url = instance.get('repo_clone_url')
            html_url = instance.get('repo_html_url')
            creden = {
                'git_repo_url': html_url,
                'git_repo_clone_url': clone_url
            }
            return GetBindingSpec(credentials=creden)
        else:
            raise errors.ErrBindingDoesNotExist()


def create_broker_blueprint(credentials: api.BrokerCredentials):
    return api.get_blueprint(Broker("Jenkins-Broker","Jenkins-Plan-GID"), credentials, logger)
