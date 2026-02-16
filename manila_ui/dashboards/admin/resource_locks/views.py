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
from django.utils.translation import gettext_lazy as _

from manila_ui.dashboards.admin.resource_locks import tabs as admin_tabs
from manila_ui.dashboards.project.resource_locks import views as project_views


class IndexView(project_views.IndexView):
    tab_group_class = admin_tabs.ResourceLockTabs
    template_name = 'admin/resource_locks/index.html'
    page_title = _("Resource Locks")


class UpdateLockView(project_views.UpdateLockView):
    submit_url = "horizon:admin:resource_locks:update"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        args = (self.kwargs['lock_id'],)
        context['form_url'] = reverse(self.submit_url, args=args)
        context['submit_url'] = context['form_url']
        return context
