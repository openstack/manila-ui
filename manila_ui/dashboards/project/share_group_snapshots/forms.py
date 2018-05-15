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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila


class CreateShareGroupSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"), required=True)
    description = forms.CharField(
        widget=forms.Textarea,
        label=_("Description"),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(self.__class__, self).__init__(request, *args, **kwargs)
        # populate share_group_id
        sg_id = kwargs.get('initial', {}).get('share_group_id', [])
        self.fields['share_group_id'] = forms.CharField(
            widget=forms.HiddenInput(), initial=sg_id)

    def handle(self, request, data):
        try:
            snapshot = manila.share_group_snapshot_create(
                request,
                data['share_group_id'], data['name'], data['description'])
            message = _('Creating share group snapshot "%s".') % data['name']
            messages.success(request, message)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:share_group_snapshots:index")
            exceptions.handle(
                request,
                _('Unable to create share group snapshot.'),
                redirect=redirect)
        return False


class UpdateShareGroupSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length="255", label=_("Name"))
    description = forms.CharField(
        widget=forms.Textarea, label=_("Description"), required=False)

    def handle(self, request, data):
        sgs_id = self.initial['share_group_snapshot_id']
        try:
            manila.share_group_snapshot_update(
                request, sgs_id, data['name'], data['description'])
            message = _('Updating share group snapshot "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:share_group_snapshots:index")
            exceptions.handle(
                request, _('Unable to update share group snapshot.'),
                redirect=redirect)
        return False
