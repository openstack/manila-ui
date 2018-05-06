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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila


class CreateShareSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Snapshot Name"))
    description = forms.CharField(
        widget=forms.Textarea,
        label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(self.__class__, self).__init__(request, *args, **kwargs)
        # populate share_id
        share_id = kwargs.get('initial', {}).get('share_id', [])
        self.fields['share_id'] = forms.CharField(
            widget=forms.HiddenInput(), initial=share_id)

    def handle(self, request, data):
        try:
            snapshot = manila.share_snapshot_create(
                request, data['share_id'], data['name'], data['description'])
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
