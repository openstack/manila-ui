# Copyright 2017 Mirantis, Inc.
# All rights reserved.
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


SGT_GROUP_SPECS_FORM_ATTRS = {
    "rows": 5,
    "cols": 40,
    "style": "height: 135px; width: 100%;",  # in case 'rows' not picked up
}


class CreateShareGroupTypeForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"), required=True)
    group_specs = forms.CharField(
        required=False, label=_("Group specs"),
        widget=forms.widgets.Textarea(attrs=SGT_GROUP_SPECS_FORM_ATTRS))
    share_types = forms.MultipleChoiceField(
        label=_("Share Types"),
        required=True,
        widget=forms.SelectMultiple(attrs={
            "style": "height: 155px;",
        }),
        error_messages={
            'required': _("At least one share type must be specified.")
        })
    is_public = forms.BooleanField(
        label=_("Public"), required=False, initial=True,
        help_text=("Defines whether this share group type is available for "
                   "all or not. List of allowed tenants should be set "
                   "separately."))

    def __init__(self, request, *args, **kwargs):
        super(self.__class__, self).__init__(request, *args, **kwargs)
        manila_features = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
        self.enable_public_share_group_type_creation = manila_features.get(
            'enable_public_share_group_type_creation', True)
        if not self.enable_public_share_group_type_creation:
            self.fields.pop('is_public')
        share_type_choices = manila.share_type_list(request)
        self.fields['share_types'].choices = [
            (choice.id, choice.name) for choice in share_type_choices]

    def clean(self):
        cleaned_data = super(CreateShareGroupTypeForm, self).clean()
        return cleaned_data

    def handle(self, request, data):
        try:
            set_dict, unset_list = utils.parse_str_meta(data['group_specs'])
            if unset_list:
                msg = _("Expected only pairs of key=value.")
                raise ValidationError(message=msg)

            is_public = (
                self.enable_public_share_group_type_creation and
                data["is_public"])
            share_group_type = manila.share_group_type_create(
                request, data["name"], share_types=data['share_types'],
                is_public=is_public)
            if set_dict:
                manila.share_group_type_set_specs(
                    request, share_group_type.id, set_dict)

            msg = _("Successfully created share group type: "
                    "%s") % share_group_type.name
            messages.success(request, msg)
            return True
        except ValidationError as e:
            # handle error without losing dialog
            self.api_error(e.messages[0])
            return False
        except Exception:
            exceptions.handle(request, _('Unable to create share group type.'))
            return False


class UpdateShareGroupTypeForm(forms.SelfHandlingForm):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # NOTE(vponomaryov): parse existing group specs
        #                    to str view for textarea html element
        es_str = ""
        for k, v in self.initial["group_specs"].items():
            es_str += "%s=%s\r\n" % (k, v)
        self.initial["group_specs"] = es_str

    group_specs = forms.CharField(
        required=False, label=_("Group specs"),
        widget=forms.widgets.Textarea(attrs=SGT_GROUP_SPECS_FORM_ATTRS))

    def handle(self, request, data):
        try:
            set_dict, unset_list = utils.parse_str_meta(data['group_specs'])
            if set_dict:
                manila.share_group_type_set_specs(
                    request, self.initial["id"], set_dict)
            if unset_list:
                get = manila.share_group_type_get_specs(
                    request, self.initial["id"])

                # NOTE(vponomaryov): skip keys that are already unset
                to_unset = set(unset_list).intersection(set(get.keys()))
                if to_unset:
                    manila.share_group_type_unset_specs(
                        request, self.initial["id"], to_unset)
            msg = _(
                "Successfully updated group specs for share group type '%s'.")
            msg = msg % self.initial['name']
            messages.success(request, msg)
            return True
        except ValidationError as e:
            # handle error without losing dialog
            self.api_error(e.messages[0])
            return False
        except Exception:
            msg = _("Unable to update group_specs for share group type.")
            exceptions.handle(request, msg)
            return False
