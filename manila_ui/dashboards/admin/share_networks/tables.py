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
from horizon import tables

import manila_ui.dashboards.project.share_networks.tables as sn_tables


class ShareNetworksTable(tables.DataTable):
    name = tables.WrappingColumn(
        "name", verbose_name=_("Name"),
        link="horizon:admin:share_networks:share_network_detail")
    project = tables.Column("project_name", verbose_name=_("Project"))

    def get_object_display(self, share_network):
        return share_network.name or str(share_network.id)

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta(object):
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (
            tables.NameFilterAction,
            sn_tables.Delete,
        )
        row_class = sn_tables.UpdateRow
        row_actions = (
            sn_tables.Delete,
        )
