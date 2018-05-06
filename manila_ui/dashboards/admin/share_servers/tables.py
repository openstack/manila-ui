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

from django.template.defaultfilters import title
from django.urls import reverse
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from horizon import tables
import six

from manila_ui.api import manila


class DeleteShareServer(tables.DeleteAction):
    policy_rules = (("share", "share_server:delete"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Share Server",
            u"Delete Share Server",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Share Server",
            u"Deleted Share Server",
            count
        )

    def delete(self, request, obj_id):
        manila.share_server_delete(request, obj_id)

    def allowed(self, request, share_serv):
        if share_serv:
            share_search_opts = {'share_server_id': share_serv.id}
            shares_list = manila.share_list(
                request, search_opts=share_search_opts)
            if shares_list:
                return False
            return share_serv.status not in ("deleting", "creating")
        return True


class UpdateShareServerRow(tables.Row):
    ajax = True

    def get_data(self, request, share_serv_id):
        share_serv = manila.share_server_get(request, share_serv_id)
        return share_serv


class ShareServersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("deleting", None),
        ("creating", None),
        ("error", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("in-use", pgettext_lazy("Current status of share server", u"In-use")),
        ("active", pgettext_lazy("Current status of share server", u"Active")),
        ("creating", pgettext_lazy("Current status of share server",
                                   u"Creating")),
        ("error", pgettext_lazy("Current status of share server",
                                u"Error")),
    )
    uid = tables.Column(
        "id", verbose_name=_("Id"),
        link="horizon:admin:share_servers:share_server_detail")
    host = tables.Column("host", verbose_name=_("Host"))
    project = tables.Column("project_name", verbose_name=_("Project"))

    def get_share_server_link(share_serv):
        if hasattr(share_serv, 'share_network_id'):
            return reverse("horizon:admin:share_networks:share_network_detail",
                           args=(share_serv.share_network_id,))
        else:
            return None

    share_net_name = tables.Column(
        "share_network_name", verbose_name=_("Share Network"),
        link=get_share_server_link)
    status = tables.Column(
        "status", verbose_name=_("Status"),
        status=True, filters=(title,), status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES)

    def get_object_display(self, share_server):
        return six.text_type(share_server.id)

    def get_object_id(self, share_server):
        return six.text_type(share_server.id)

    class Meta(object):
        name = "share_servers"
        status_columns = ["status"]
        verbose_name = _("Share Server")
        table_actions = (
            tables.NameFilterAction,
            DeleteShareServer,
        )
        row_class = UpdateShareServerRow
        row_actions = (
            DeleteShareServer,
        )
