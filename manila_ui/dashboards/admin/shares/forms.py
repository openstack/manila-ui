# Copyright (c) 2014 NetApp, Inc.
# All Rights Reserved.
#
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

from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila
from manila_ui.dashboards import utils

from openstack_dashboard.api import keystone
from openstack_dashboard.api import neutron


ST_EXTRA_SPECS_FORM_ATTRS = {
    "rows": 5,
    "cols": 40,
    "style": "height: 135px; width: 100%;",  # in case 'rows' not picked up
}


class CreateShareType(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    spec_driver_handles_share_servers = forms.CharField(
        max_length="5", label=_("Driver handles share servers"))
    extra_specs = forms.CharField(required=False, label=_("Extra specs"),
        widget=forms.widgets.Textarea(attrs=ST_EXTRA_SPECS_FORM_ATTRS))

    def handle(self, request, data):
        try:
            spec_dhss = data['spec_driver_handles_share_servers'].lower()
            allowed_dhss_values = ['true', 'false']
            if spec_dhss not in allowed_dhss_values:
                msg = _("Improper value set to required extra spec "
                        "'spec_driver_handles_share_servers'. "
                        "Allowed values are %s. "
                        "Case insensitive.") % allowed_dhss_values
                raise ValidationError(message=msg)

            set_dict, unset_list = utils.parse_str_meta(data['extra_specs'])
            if unset_list:
                msg = _("Expected only pairs of key=value.")
                raise ValidationError(message=msg)

            share_type = manila.share_type_create(
                request, data["name"], spec_dhss)
            if set_dict:
                manila.share_type_set_extra_specs(
                    request, share_type.id, set_dict)

            msg = _("Successfully created share type: %s") % share_type.name
            messages.success(request, msg)
            return True
        except ValidationError as e:
            # handle error without losing dialog
            self.api_error(e.messages[0])
            return False
        except Exception:
            exceptions.handle(request, _('Unable to create share type.'))
            return False


class UpdateShareType(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        super(UpdateShareType, self).__init__(*args, **kwargs)
        # NOTE(vponomaryov): parse existing extra specs
        #                    to str view for textarea html element
        es_str = ""
        for k, v in self.initial["extra_specs"].iteritems():
            es_str += "%s=%s\r\n" % (k, v)
        self.initial["extra_specs"] = es_str

    extra_specs = forms.CharField(required=False, label=_("Extra specs"),
        widget=forms.widgets.Textarea(attrs=ST_EXTRA_SPECS_FORM_ATTRS))

    def handle(self, request, data):
        try:
            set_dict, unset_list = utils.parse_str_meta(data['extra_specs'])
            if set_dict:
                manila.share_type_set_extra_specs(
                    request, self.initial["id"], set_dict)
            if unset_list:
                get = manila.share_type_get_extra_specs(
                    request, self.initial["id"])
                for unset_key in unset_list:
                    # NOTE(vponomaryov): skip keys that are already unset
                    if unset_key in get.keys():
                        manila.share_type_unset_extra_specs(
                            request, self.initial["id"], unset_key)
            msg = _("Successfully updated extra specs for share type '%s'.")
            msg = msg % self.initial['name']
            messages.success(request, msg)
            return True
        except ValidationError as e:
            # handle error without losing dialog
            self.api_error(e.messages[0])
            return False
        except Exception:
            msg = _("Unable to update extra_specs for share type.")
            exceptions.handle(request, msg)
            return False


class CreateSecurityService(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    dns_ip = forms.CharField(max_length="15", label=_("DNS IP"))
    server = forms.CharField(max_length="255", label=_("Server"))
    domain = forms.CharField(max_length="255", label=_("Domain"))
    user = forms.CharField(max_length="255", label=_("User"))
    password = forms.CharField(max_length="255", label=_("Password"))
    type = forms.ChoiceField(choices=(("", ""),
                                      ("active_directory", "Active Directory"),
                                      ("ldap", "LDAP"),
                                      ("kerberos", "Kerberos")),
                             label=_("Type"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            security_service = manila.security_service_create(
                request, **data)
            messages.success(request,
                             _('Successfully created security service: %s')
                             % data['name'])
            return security_service
        except Exception:
            exceptions.handle(request,
                              _('Unable to create security service.'))
            return False


class CreateShareNetworkForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    neutron_net_id = forms.ChoiceField(choices=(), label=_("Neutron Net ID"))
    neutron_subnet_id = forms.ChoiceField(choices=(),
                                          label=_("Neutron Subnet ID"))
    #security_service = forms.MultipleChoiceField(
    #    widget=forms.SelectMultiple,
    #    label=_("Security Service"))
    project = forms.ChoiceField(choices=(), label=_("Project"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateShareNetworkForm, self).__init__(
            request, *args, **kwargs)
        net_choices = neutron.network_list(request)
        subnet_choices = neutron.subnet_list(request)
        self.fields['neutron_net_id'].choices = [(' ', ' ')] + \
                                                [(choice.id, choice.name_or_id)
                                                 for choice in net_choices]
        self.fields['neutron_subnet_id'].choices = [(' ', ' ')] + \
                                                   [(choice.id,
                                                     choice.name_or_id) for
                                                    choice in subnet_choices]
        tenants, has_more = keystone.tenant_list(request)
        self.fields['project'].choices = [(' ', ' ')] + \
                                                   [(choice.id,
                                                     choice.name) for
                                                    choice in tenants]

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            share_network = manila.share_network_create(request, **data)
            messages.success(request,
                             _('Successfully created share network: %s')
                             % data['name'])
            return share_network
        except Exception:
            exceptions.handle(request,
                              _('Unable to create share network.'))
            return False
