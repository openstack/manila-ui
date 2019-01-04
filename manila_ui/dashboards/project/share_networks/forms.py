# Copyright (c) 2014 NetApp, Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.api import network


class Create(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    description = forms.CharField(
        widget=forms.Textarea, label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(Create, self).__init__(request, *args, **kwargs)
        self.neutron_enabled = base.is_service_enabled(request, 'network')
        net_choices = network.network_list(request)
        if self.neutron_enabled:
            self.fields['neutron_net_id'] = forms.ChoiceField(
                choices=[(' ', ' ')] + [(choice.id, choice.name_or_id)
                                        for choice in net_choices],
                label=_("Neutron Net"), widget=forms.Select(
                    attrs={'class': 'switchable', 'data-slug': 'net'}))
            for net in net_choices:
                # For each network create switched choice field with
                # the its subnet choices
                subnet_field_name = 'subnet-choices-%s' % net.id
                subnet_field = forms.ChoiceField(
                    choices=(), label=_("Neutron Subnet"),
                    widget=forms.Select(attrs={
                        'class': 'switched',
                        'data-switch-on': 'net',
                        'data-net-%s' % net.id: _("Neutron Subnet")
                    }))
                self.fields[subnet_field_name] = subnet_field
                subnet_choices = neutron.subnet_list(
                    request, network_id=net.id)
                self.fields[subnet_field_name].choices = [
                    (' ', ' ')] + [(choice.id, choice.name_or_id)
                                   for choice in subnet_choices]
        else:
            self.fields['nova_net_id'] = forms.ChoiceField(
                choices=[(' ', ' ')] + [(choice.id, choice.name_or_id)
                                        for choice in net_choices],
                label=_("Nova Net"), widget=forms.Select(
                    attrs={'class': 'switched', 'data-slug': 'net'}))

    def handle(self, request, data):
        try:
            send_data = {'name': data['name']}
            if data['description']:
                send_data['description'] = data['description']
            share_net_id = data.get('neutron_net_id', data.get('nova_net_id'))
            share_net_id = share_net_id.strip()
            if self.neutron_enabled and share_net_id:
                send_data['neutron_net_id'] = share_net_id
                subnet_key = 'subnet-choices-%s' % share_net_id
                if subnet_key in data:
                    send_data['neutron_subnet_id'] = data[subnet_key]
            elif not self.neutron_enabled and share_net_id:
                send_data['nova_net_id'] = data['nova_net_id']
            share_network = manila.share_network_create(request, **send_data)
            messages.success(request, _('Successfully created share'
                                        ' network: %s') % send_data['name'])
            return share_network
        except Exception:
            exceptions.handle(request, _('Unable to create share network.'))
            return False


class Update(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def handle(self, request, data, *args, **kwargs):
        share_net_id = self.initial['share_network_id']
        try:
            manila.share_network_update(request, share_net_id,
                                        name=data['name'],
                                        description=data['description'])

            message = _('Updating share network "%s"') % data['name']
            messages.info(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update share network.'),
                              redirect=redirect)


class AddSecurityServiceForm(forms.SelfHandlingForm):
    sec_service = forms.MultipleChoiceField(
        label=_("Networks"),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        error_messages={
            'required': _(
                "At least one security service"
                " must be specified.")})

    def __init__(self, request, *args, **kwargs):
        super(AddSecurityServiceForm, self).__init__(
            request, *args, **kwargs)
        sec_services_choices = manila.security_service_list(request)
        self.fields['sec_service'].choices = [(' ', ' ')] + \
                                             [(choice.id, choice.name or
                                              choice.id) for choice in
                                              sec_services_choices]

    def handle(self, request, data):
        pass
