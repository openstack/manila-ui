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


from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from manila_ui.api import manila


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
