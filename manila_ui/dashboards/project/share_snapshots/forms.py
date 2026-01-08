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

"""
Views for managing share snapshots.
"""

from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila
from manila_ui.dashboards import utils


class CreateShareSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Snapshot Name"))
    description = forms.CharField(
        widget=forms.Textarea,
        label=_("Description"), required=False)
    metadata = forms.CharField(
        label=_("Metadata"), required=False,
        widget=forms.Textarea(attrs={'rows': 4}))

    def __init__(self, request, *args, **kwargs):
        super(self.__class__, self).__init__(request, *args, **kwargs)
        # populate share_id
        share_id = kwargs.get('initial', {}).get('share_id', [])
        self.fields['share_id'] = forms.CharField(
            widget=forms.HiddenInput(), initial=share_id)

    def handle(self, request, data):
        metadata = {}
        try:
            set_dict, unset_list = utils.parse_str_meta(data['metadata'])
            if unset_list:
                msg = _("Expected only pairs of key=value.")
                raise ValidationError(message=msg)
            metadata = set_dict
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        try:
            snapshot = manila.share_snapshot_create(
                request,
                data['share_id'],
                name=data['name'],
                description=data['description'],
                metadata=metadata)
            message = _('Creating share snapshot "%s".') % data['name']
            messages.success(request, message)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:share_snapshots:index")
            exceptions.handle(request,
                              _('Unable to create share snapshot.'),
                              redirect=redirect)


class UpdateShareSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Snapshot Name"))
    description = forms.CharField(
        widget=forms.Textarea, label=_("Description"), required=False)

    def handle(self, request, data):
        snapshot_id = self.initial['snapshot_id']
        try:
            manila.share_snapshot_update(
                request, snapshot_id, data['name'], data['description'])
            message = _('Updating share snapshot "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            exceptions.handle(request, _('Unable to update share snapshot.'))


class AddShareSnapshotRule(forms.SelfHandlingForm):
    access_type = forms.ChoiceField(
        label=_("Access Type"), required=True,
        choices=(('ip', 'ip'), ('user', 'user'), ('cephx', 'cephx'),
                 ('cert', 'cert')))
    access_to = forms.CharField(
        label=_("Access To"), max_length="255", required=True)

    def handle(self, request, data):
        snapshot_id = self.initial['snapshot_id']
        try:
            manila.share_snapshot_allow(
                request, snapshot_id,
                access_to=data['access_to'],
                access_type=data['access_type'])
            message = _('Creating snapshot rule for "%s"') % data['access_to']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse(
                "horizon:project:share_snapshots:share_snapshot_manage_rules",
                args=[self.initial['snapshot_id']])
            exceptions.handle(
                request, _('Unable to add snapshot rule.'), redirect=redirect)


class UpdateSnapshotMetadataForm(forms.SelfHandlingForm):
    snapshot_id = forms.CharField(widget=forms.HiddenInput())
    metadata = forms.CharField(label=_("Metadata"),
                               widget=forms.Textarea(attrs={'rows': 10}),
                               required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meta_str = ""
        for k, v in self.initial["metadata"].items():
            meta_str += f"{k}={v}\r\n"
        self.initial["metadata"] = meta_str

    def handle(self, request, data):
        snapshot_id = data['snapshot_id']
        try:
            set_dict, unset_list = utils.parse_str_meta(data['metadata'])
            if unset_list:
                manila.share_snapshot_delete_metadata(
                    request, snapshot_id, unset_list)
            if set_dict:
                manila.share_snapshot_set_metadata(
                    request, snapshot_id, set_dict)
            messages.success(request, _('Snapshot metadata updated.'))
            return True
        except Exception as e:
            if "MetadataItemNotFound" in str(e) or getattr(
                e, 'code', None) == 404:
                msg = _("Invalid format: Each line must contain a 'key=value' "
                        "pair. If you intended to delete a key, ensure the "
                        "key exists.")
                messages.error(request, msg)
            else:
                exceptions.handle(
                    request, _('Unable to update snapshot metadata.'))
            return False
