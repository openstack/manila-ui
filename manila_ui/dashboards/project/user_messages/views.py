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
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
from manila_ui.dashboards.project.user_messages import tables as um_tables
from manila_ui.dashboards.project.user_messages import tabs as um_tabs


class UserMessagesView(tables.MultiTableView):
    table_classes = (
        um_tables.UserMessagesTable,
    )
    template_name = "project/user_messages/index.html"
    page_title = _("User Messages")

    @memoized.memoized_method
    def get_user_messages_data(self):
        try:
            messages = manila.messages_list(self.request)
        except Exception:
            msg = _("Unable to retrieve messages list.")
            exceptions.handle(self.request, msg)
            return []
        return messages


class UserMessagesDetailView(tabs.TabView):
    tab_group_class = um_tabs.UserMessagesDetailTabs
    template_name = 'project/user_messages/detail.html'
    redirect_url = reverse_lazy('horizon:project:user_messages:index')

    def get_context_data(self, **kwargs):
        context = super(UserMessagesDetailView, self).get_context_data(
            **kwargs)
        message = self.get_data()
        message_id = message.id
        context["message"] = message
        context["message_id"] = message_id
        context["page_title"] = _("User Message Details: "
                                  "%(message_id)s") % (
            {'message_id': message_id})
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            message_id = self.kwargs['message_id']
            message = manila.messages_get(self.request, message_id)
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve user message detail.'),
                redirect=self.redirect_url)
        return message

    def get_tabs(self, request, *args, **kwargs):
        message = self.get_data()
        return self.tab_group_class(request, message=message, **kwargs)
