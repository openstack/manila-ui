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
Views for managing snapshots.
"""

from django.core.urlresolvers import reverse
from django.forms import ValidationError  # noqa
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.http import urlencode  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila


class CreateSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Snapshot Name"))
    description = forms.CharField(
        widget=forms.Textarea,
        label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateSnapshotForm, self).__init__(request, *args, **kwargs)

        # populate share_id
        share_id = kwargs.get('initial', {}).get('share_id', [])
        self.fields['share_id'] = forms.CharField(widget=forms.HiddenInput(),
                                                  initial=share_id)

    def handle(self, request, data):
        try:
            snapshot = manila.share_snapshot_create(
                request, data['share_id'], data['name'], data['description'])
            message = _('Creating share snapshot "%s".') % data['name']
            messages.success(request, message)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to create share snapshot.'),
                              redirect=redirect)


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def handle(self, request, data):
        snapshot_id = self.initial['snapshot_id']
        try:
            manila.share_snapshot_update(
                request, snapshot_id, name=data['name'],
                description=data['description'])
            message = _('Updating snapshot "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            redirect = "?".join([reverse("horizon:project:shares:index"),
                                 urlencode({"tab": "snapshots"})])
            exceptions.handle(request,
                              _('Unable to update snapshot.'),
                              redirect=redirect)
