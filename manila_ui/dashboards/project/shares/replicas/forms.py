# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.
#
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

from manila_ui.api import manila


class CreateReplicaForm(forms.SelfHandlingForm):
    availability_zone = forms.ChoiceField(
        label=_("Availability Zone"),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateReplicaForm, self).__init__(request, *args, **kwargs)

        # populate share_id
        share_id = kwargs.get('initial', {}).get('share_id', [])
        self.fields['share_id'] = forms.CharField(widget=forms.HiddenInput(),
                                                  initial=share_id)

        availability_zones = manila.availability_zone_list(request)
        self.fields['availability_zone'].choices = (
            [(az.name, az.name) for az in availability_zones])

    def handle(self, request, data):
        try:
            replica = manila.share_replica_create(request,
                                                  data['share_id'],
                                                  data['availability_zone'])
            message = _('Creating replica for share "%s".') % data['share_id']
            messages.success(request, message)
            return replica
        except Exception:
            redirect = reverse("horizon:project:shares:manage_replicas",
                               args=[data['share_id']])
            exceptions.handle(request,
                              _('Unable to create share replica.'),
                              redirect=redirect)


class SetReplicaAsActiveForm(forms.SelfHandlingForm):
    def handle(self, request, data):
        replica_id = self.initial['replica_id']
        try:
            replica = manila.share_replica_get(self.request, replica_id)
            manila.share_replica_promote(request, replica)
            message = _('Setting replica "%s" as active...') % replica_id
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(
                request,
                _("Unable to set replica '%s' as active.") % replica_id,
                redirect=redirect)
