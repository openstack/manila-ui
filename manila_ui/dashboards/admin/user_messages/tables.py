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

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from manila_ui.dashboards.project.user_messages import tables as project_tables


class DeleteUserMessage(project_tables.DeleteUserMessage):
    pass


class UserMessageIDColumn(project_tables.UserMessageIDColumn):
    pass


class UserMessagesAdminTable(project_tables.UserMessagesTable):
    project_name = tables.Column(
        "project_name",
        verbose_name=_("Project"),
    )

    class Meta(object):
        name = "user_messages"
        verbose_name = _("User Messages")
        table_actions = (
            tables.NameFilterAction,
            DeleteUserMessage,
        )
        row_actions = (
            DeleteUserMessage,
        )
        columns = (
            'project_name', 'message_id', 'message_level',
            'resource_type',
            'resource_id', 'user_message', 'created_at',
        )
