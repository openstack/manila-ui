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
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tabs

from manila_ui.api import manila
from manila_ui.dashboards.project.resource_locks import forms as rl_forms
from manila_ui.dashboards.project.resource_locks import tabs as rl_tabs


class IndexView(tabs.TabbedTableView):
    tab_group_class = rl_tabs.ResourceLockTabs
    template_name = 'project/resource_locks/index.html'
    page_title = _("Resource Locks")


class UpdateLockView(forms.ModalFormView):
    form_class = rl_forms.UpdateLockForm
    form_id = "update_lock_form"
    modal_header = _("Edit Lock Reason")
    submit_label = _("Save Changes")
    submit_url = "horizon:project:resource_locks:update"
    template_name = 'project/resource_locks/update_lock.html'
    context_object_name = 'lock'
    success_url = reverse_lazy('horizon:project:resource_locks:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        args = (self.kwargs['lock_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        lock_id = self.kwargs['lock_id']
        try:
            lock = manila.resource_lock_get(self.request, lock_id)
            self.resource_type = getattr(lock, 'resource_type', '').lower()
            return {'lock_id': lock.id,
                    'lock_reason': lock.lock_reason}
        except Exception:
            exceptions.handle(
                self.request, _("Unable to retrieve lock details."))

    def get_success_url(self):
        resource_type = getattr(self, 'resource_type', None)
        namespace = self.request.resolver_match.namespace
        if not namespace.startswith('horizon:'):
            namespace = f"horizon:{namespace}"
        base_url = reverse(f"{namespace}:index")
        if resource_type == 'access_rule':
            return f"{base_url}?tab=resource_lock_tabs__rules_tab"
        return f"{base_url}?tab=resource_lock_tabs__shares_tab"
