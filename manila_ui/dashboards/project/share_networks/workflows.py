#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows
from openstack_dashboard import api
from openstack_dashboard.api import base

from manila_ui.api import manila
from manila_ui.dashboards import utils


class CreateShareNetworkInfoAction(workflows.Action):
    share_network_name = forms.CharField(
        max_length=255, label=_("Name"), required=True)
    share_network_description = forms.CharField(
        widget=forms.Textarea, label=_("Description"), required=False)

    class Meta(object):
        name = ("Share Network")


class CreateShareNetworkInfoStep(workflows.Step):
    action_class = CreateShareNetworkInfoAction
    contributes = ("share_network_description",
                   "share_network_name")


class AddShareNetworkSubnetAction(workflows.MembershipAction):

    availability_zone = forms.ChoiceField(
        required=False,
        label=_('Availability Zone'),
        widget=forms.ThemableSelectWidget(attrs={
            'data-availability_zone': _('Availability Zone')}))

    neutron_net_id = forms.ChoiceField(
        required=False,
        label=_('Neutron Net'),
        widget=forms.ThemableSelectWidget(attrs={
            'class': 'switchable',
            'data-slug': 'neutron_net_id',
            'data-neutron_net_id': _('Neutron Net')}))

    class Meta(object):
        name = _("Subnet")
        help_text = _("Specify an Availability Zone or an existing subnet. "
                      "If no details are specified, "
                      "then a default subnet with a null Availability "
                      "Zone will be created automatically.")

    def __init__(self, request, context, *args, **kwargs):
        super().__init__(request, context, *args, **kwargs)

        self.fields['availability_zone'].choices = (
            self.get_availability_zone_choices(request)
        )
        self.neutron_enabled = base.is_service_enabled(request, 'network')
        if self.neutron_enabled:
            try:
                self.fields['neutron_net_id'].choices, networks = (
                    self.get_neutron_net_id_choices(request)
                )
            except Exception:
                msg = _('Unable to initialize neutron networks.')
                exceptions.handle(request, msg)
            try:
                self.get_neutron_subnet_id_choices(request, networks)
            except Exception:
                msg = _('Unable to initialize neutron subnets.')
                exceptions.handle(request, msg)

    def get_availability_zone_choices(self, request):
        availability_zone_choices = [('', _('None'))]

        for availability_zone in manila.availability_zone_list(request):
            availability_zone_choices.append(
                (availability_zone.id, availability_zone.name)
            )
        return availability_zone_choices

    def get_neutron_net_id_choices(self, request):
        net_choices = [('', _('None'))]

        networks = api.neutron.network_list(request)
        for network in networks:
            net_choices.append((utils.transform_dashed_name(network.id),
                                network.name_or_id))
        return net_choices, networks

    def get_neutron_subnet_id_choices(self, request, networks):
        for net in networks:
            subnet_field_name = (
                'subnet-choices-%s' % utils.transform_dashed_name(net.id))
            data_net_id = (
                'data-neutron_net_id-%s' % utils.transform_dashed_name(net.id))
            subnet_field = forms.ChoiceField(
                required=False,
                choices=(),
                label=_('Neutron Subnet'),
                widget=forms.ThemableSelectWidget(attrs={
                    'class': 'switched',
                    'data-switch-on': 'neutron_net_id',
                    data_net_id: _('Neutron Subnet')}))
            self.fields[subnet_field_name] = subnet_field
            subnet_choices = api.neutron.subnet_list(request,
                                                     network_id=net.id)
            self.fields[subnet_field_name].choices = [
                (choice.id, choice.name_or_id)
                for choice in subnet_choices]

    def hide_neutron_subnet_id_choices(self):
        self.fields['neutron_subnet_id'].choices = []
        self.fields['neutron_subnet_id'].widget = forms.HiddenInput()


class AddShareNetworkSubnetStep(workflows.Step):
    action_class = AddShareNetworkSubnetAction
    contributes = ("neutron_net_id", "neutron_subnet_id", "availability_zone")


class CreateShareNetworkWorkflow(workflows.Workflow):
    slug = "create_share_network"
    name = _("Create Share Network")
    finalize_button_name = _("Create Share Network")
    success_message = _('Created share network "%s".')
    failure_message = _('Unable to create share network "%s".')
    success_url = 'horizon:project:share_networks:index'
    default_steps = (CreateShareNetworkInfoStep, AddShareNetworkSubnetStep)
    wizard = True

    def handle(self, request, context):
        try:
            data = request.POST
            send_data = {'name': context['share_network_name']}
            if context['share_network_description']:
                send_data['description'] = context['share_network_description']
            neutron_net_id = context.get('neutron_net_id')
            if neutron_net_id:
                send_data['neutron_net_id'] = utils.transform_dashed_name(
                    neutron_net_id.strip())
                subnet_key = (
                    'subnet-choices-%s' % neutron_net_id.strip()
                )
                if data.get(subnet_key) is not None:
                    send_data['neutron_subnet_id'] = data.get(subnet_key)
            if context['availability_zone']:
                send_data['availability_zone'] = context['availability_zone']
            share_network = manila.share_network_create(request, **send_data)
            messages.success(request, _('Successfully created share'
                                        ' network: %s') % send_data['name'])
            return share_network
        except Exception:
            exceptions.handle(request, _('Unable to create share network.'))
            return False


class UpdateShareNetworkInfoAction(workflows.Action):
    name = forms.CharField(label=_("Name"),
                           max_length=255)

    description = forms.CharField(label=_("Description"),
                                  max_length=255,
                                  required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdateShareNetworkInfoAction, self).__init__(
            request, *args, **kwargs)
        share_network = manila.share_network_get(request,
                                                 self.initial['id'])
        self.fields['name'].initial = share_network.name
        self.fields['description'].initial = share_network.description

    class Meta(object):
        name = _("Share Network Info")
        help_text = _("From here you can update share network info. ")
        slug = "update-share_network_info"

    def clean(self):
        cleaned_data = super(UpdateShareNetworkInfoAction, self).clean()
        return cleaned_data


class UpdateShareNetworkInfoStep(workflows.Step):
    action_class = UpdateShareNetworkInfoAction
    contributes = ("description",
                   "name")


class AddSecurityServiceAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(AddSecurityServiceAction, self).__init__(request,
                                                       *args,
                                                       **kwargs)
        err_msg = _('Unable to get the security services hosts')

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        share_network_id = self.initial['id']
        security_services = manila.share_network_security_service_list(
            request, share_network_id)
        sec_services_initial = [sec_service.id for sec_service
                                in security_services]
        sec_services = []
        try:
            sec_services = manila.security_service_list(request)
        except Exception:
            exceptions.handle(request, err_msg)

        sec_services_choices = [(sec_service.id,
                                 sec_service.name or sec_service.id)
                                for sec_service in sec_services]
        self.fields[field_name].choices = sec_services_choices
        self.fields[field_name].initial = sec_services_initial

    class Meta(object):
        name = _("Security services within share network")
        slug = "add_security_service"


class AddSecurityServiceStep(workflows.UpdateMembersStep):
    action_class = AddSecurityServiceAction
    help_text = _("Add security services to share network.")
    available_list_title = _("Available security services")
    members_list_title = _("Selected security services")
    no_available_text = _("No security services found.")
    no_members_text = _("No security services selected.")
    show_roles = False
    depends_on = ("id",)
    contributes = ("security_services",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['security_service'] = data.get(member_field_name, [])
        return context


class UpdateShareNetworkWorkflow(workflows.Workflow):
    slug = "update_share_network"
    name = _("Update Share Network")
    finalize_button_name = _("Update Share Network")
    success_message = _('Updated share network "%s".')
    failure_message = _('Unable to update share network "%s".')
    success_url = 'horizon:project:share_networks:index'
    default_steps = (UpdateShareNetworkInfoStep, AddSecurityServiceStep)

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, context):
        try:
            manila.share_network_update(request, context['id'],
                                        description=context['description'],
                                        name=context['name'])
            sec_services = manila.security_service_list(request, search_opts={
                'share_network_id': context['id']})
            sec_services_old = set([sec_service.id
                                   for sec_service in sec_services])
            sec_services_new = set(context['security_service'])
            for sec_service in sec_services_new - sec_services_old:
                manila.share_network_security_service_add(request,
                                                          context['id'],
                                                          sec_service)
            for sec_service in sec_services_old - sec_services_new:
                manila.share_network_security_service_remove(request,
                                                             context['id'],
                                                             sec_service)
            return True
        except Exception:
            exceptions.handle(request, _('Unable to update share network.'))
            return False
