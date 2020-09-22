# Copyright (c) 2020 Red Hat, Inc.
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

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.admin.user_messages import tables as admin_tables
from manila_ui.dashboards.admin.user_messages import tabs as admin_tabs
from manila_ui.dashboards.admin import utils
from manila_ui.dashboards.project.user_messages import views as project_views


class UserMessagesAdminView(project_views.UserMessagesView):
    table_classes = (
        admin_tables.UserMessagesAdminTable,
    )
    template_name = "admin/user_messages/index.html"

    @memoized.memoized_method
    def get_user_messages_data(self):
        try:
            messages = manila.messages_list(self.request)
            utils.set_project_name_to_objects(self.request, messages)
        except Exception:
            msg = _("Unable to retrieve messages list.")
            exceptions.handle(self.request, msg)
            return []
        return messages


class UserMessagesAdminDetailView(project_views.UserMessagesDetailView):
    tab_group_class = admin_tabs.UserMessagesDetailTabs
    template_name = 'admin/user_messages/detail.html'
    redirect_url = reverse_lazy('horizon:admin:user_messages:index')
