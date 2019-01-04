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

from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila
from manila_ui.dashboards import utils


ST_EXTRA_SPECS_FORM_ATTRS = {
    "rows": 5,
    "cols": 40,
    "style": "height: 135px; width: 100%;",  # in case 'rows' not picked up
}


class CreateShareType(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"), required=True)
    spec_driver_handles_share_servers = forms.ChoiceField(
        label=_("Driver handles share servers"), required=True,
        choices=(('False', 'False'), ('True', 'True')))
    extra_specs = forms.CharField(
        required=False, label=_("Extra specs"),
        widget=forms.widgets.Textarea(attrs=ST_EXTRA_SPECS_FORM_ATTRS))
    is_public = forms.BooleanField(
        label=_("Public"), required=False, initial=True,
        help_text=("Defines whether this share type is available for all "
                   "or not. List of allowed tenants should be set "
                   "separately."))

    def __init__(self, *args, **kwargs):
        super(CreateShareType, self).__init__(*args, **kwargs)
        manila_features = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
        self.enable_public_share_type_creation = manila_features.get(
            'enable_public_share_type_creation', True)
        if not self.enable_public_share_type_creation:
            self.fields.pop('is_public')

    def handle(self, request, data):
        try:
            spec_dhss = data['spec_driver_handles_share_servers'].lower()
            allowed_dhss_values = ('true', 'false')
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

            is_public = (self.enable_public_share_type_creation and
                         data["is_public"])
            share_type = manila.share_type_create(
                request, data["name"], spec_dhss, is_public=is_public)
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
        for k, v in self.initial["extra_specs"].items():
            es_str += "%s=%s\r\n" % (k, v)
        self.initial["extra_specs"] = es_str

    extra_specs = forms.CharField(
        required=False, label=_("Extra specs"),
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

                # NOTE(vponomaryov): skip keys that are already unset
                to_unset = set(unset_list).intersection(set(get.keys()))
                if to_unset:
                    manila.share_type_unset_extra_specs(
                        request, self.initial["id"], to_unset)
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
