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

from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila


class UpdateLockForm(forms.SelfHandlingForm):
    lock_id = forms.CharField(widget=forms.HiddenInput())
    lock_reason = forms.CharField(
        label=_("Lock Reason"),
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text=_("Update the reason why this resource is locked."))

    def handle(self, request, data):
        try:
            manila.resource_lock_update(
                request,
                data['lock_id'],
                lock_reason=data['lock_reason']
            )
            messages.success(request, _("Lock reason updated successfully."))
            return True
        except Exception:
            exceptions.handle(request, _("Unable to update lock reason."))
            return False
