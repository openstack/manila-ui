# Copyright (c) 2016 Mirantis, Inc.
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


class ResyncReplicaForm(forms.SelfHandlingForm):
    def handle(self, request, data):
        replica_id = self.initial['replica_id']
        try:
            replica = manila.share_replica_get(self.request, replica_id)
            manila.share_replica_resync(request, replica)
            message = _("Resync'ing replica '%s'") % replica_id
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:admin:shares:index")
            exceptions.handle(
                request,
                _("Unable to resync replica '%s'.") % replica_id,
                redirect=redirect)


class ResetReplicaStatusForm(forms.SelfHandlingForm):
    replica_status = forms.ChoiceField(
        label=_("Replica State"),
        required=True,
        choices=(
            ('available', 'available'),
            ('creating', 'creating'),
            ('deleting', 'deleting'),
            ('error', 'error'),
        )
    )

    def handle(self, request, data):
        replica_id = self.initial['replica_id']
        try:
            replica = manila.share_replica_get(self.request, replica_id)
            manila.share_replica_reset_status(
                request, replica, data["replica_status"])
            message = _("Reseting replica ('%(id)s') status from '%(from)s' "
                        "to '%(to)s'.") % {
                            "id": replica_id,
                            "from": replica.replica_state,
                            "to": data["replica_status"]}
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:admin:shares:index")
            exceptions.handle(
                request,
                _("Unable to reset status of replica '%s'.") % replica_id,
                redirect=redirect)


class ResetReplicaStateForm(forms.SelfHandlingForm):
    replica_state = forms.ChoiceField(
        label=_("Replica State"),
        required=True,
        choices=(
            ('active', 'active'),
            ('in_sync', 'in_sync'),
            ('out_of_sync', 'out_of_sync'),
            ('error', 'error'),
        )
    )

    def handle(self, request, data):
        replica_id = self.initial['replica_id']
        try:
            replica = manila.share_replica_get(self.request, replica_id)
            manila.share_replica_reset_state(
                request, replica, data["replica_state"])
            message = _("Reseting replica ('%(id)s') state from '%(from)s' "
                        "to '%(to)s'.") % {
                            "id": replica_id,
                            "from": replica.replica_state,
                            "to": data["replica_state"]}
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:admin:shares:index")
            exceptions.handle(
                request,
                _("Unable to reset state of replica '%s'.") % replica_id,
                redirect=redirect)
