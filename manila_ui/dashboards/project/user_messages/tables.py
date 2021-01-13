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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import exceptions
from horizon import tables
from horizon.utils.filters import parse_isotime

from manila_ui.api import manila


def get_date(message):
    return parse_isotime(message.created_at)


class DeleteUserMessage(tables.DeleteAction):
    policy_rules = (("share", "share:delete_message"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete User Message",
            u"Delete User Messages",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted User Message",
            u"Deleted User Messages",
            count
        )

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "project_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        message_id = self.table.get_object_display(obj)
        try:
            manila.messages_delete(request, message_id)
        except Exception:
            msg = _('Unable to delete message "%s"')
            exceptions.handle(self.request, msg % message_id)
            raise


class UserMessageIDColumn(tables.Column):

    def get_link_url(self, message):
        return reverse(self.link, args=(message.message_id,))


class UserMessagesTable(tables.DataTable):
    message_id = tables.Column(
        "id",
        verbose_name=_("ID"),
        link="horizon:project:user_messages:user_messages_detail")
    message_level = tables.Column(
        "message_level",
        verbose_name=_("Message Level")
    )
    resource_type = tables.Column(
        "resource_type",
        verbose_name=_("Resource Type"))
    resource_id = tables.Column(
        "resource_id",
        verbose_name=_("Resource ID"))
    user_message = tables.Column(
        "user_message",
        verbose_name=_("User Message"))
    created_at = tables.Column(
        get_date,
        verbose_name=_("Created At"))

    def get_object_display(self, obj):
        return obj.id

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
