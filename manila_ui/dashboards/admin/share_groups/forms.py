# Copyright (c) 2017 Mirantis, Inc.
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
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila


class ResetShareGroupStatusForm(forms.SelfHandlingForm):
    status = forms.ChoiceField(
        label=_("Status"),
        required=True,
        choices=(
            ('available', 'available'),
            ('error', 'error'),
        )
    )

    def handle(self, request, data):
        sg_id = self.initial['share_group_id']
        try:
            manila.share_group_reset_state(request, sg_id, data["status"])
            message = _(
                "Reseting share group ('%(id)s') status from '%(from)s' "
                "to '%(to)s'.") % {
                    "id": (self.initial['share_group_name'] or
                           self.initial['share_group_id']),
                    "from": self.initial['share_group_status'],
                    "to": data["status"]}
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:admin:share_groups:index")
            exceptions.handle(
                request,
                _("Unable to reset status of share group '%s'.") % sg_id,
                redirect=redirect)
        return False
