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
from django.utils.translation import ugettext_lazy as _
from horizon import tables
import six


class ShareInstancesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("available", True),
        ("creating", None),
        ("deleting", None),
        ("error", False),
        ("error_deleting", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("available", u"Available"),
        ("creating", u"Creating"),
        ("deleting", u"Deleting"),
        ("error", u"Error"),
        ("error_deleting", u"Error deleting"),
    )
    uuid = tables.Column(
        "id", verbose_name=_("ID"),
        link="horizon:admin:share_instances:share_instance_detail")
    host = tables.Column("host", verbose_name=_("Host"))
    status = tables.Column(
        "status",
        verbose_name=_("Status"),
        status=True,
        status_choices=STATUS_CHOICES,
        display_choices=STATUS_DISPLAY_CHOICES)
    availability_zone = tables.Column(
        "availability_zone", verbose_name=_("Availability Zone"))

    class Meta(object):
        name = "share_instances"
        verbose_name = _("Share Instances")
        status_columns = ("status", )
        table_actions = (
            tables.NameFilterAction,)
        multi_select = False

    def get_share_network_link(share_instance):
        if getattr(share_instance, 'share_network_id', None):
            return reverse("horizon:admin:share_networks:share_network_detail",
                           args=(share_instance.share_network_id,))
        else:
            return None

    def get_share_server_link(share_instance):
        if getattr(share_instance, 'share_server_id', None):
            return reverse("horizon:admin:share_servers:share_server_detail",
                           args=(share_instance.share_server_id,))
        else:
            return None

    def get_share_link(share_instance):
        if getattr(share_instance, 'share_id', None):
            return reverse("horizon:admin:shares:detail",
                           args=(share_instance.share_id,))
        else:
            return None

    share_net_id = tables.Column(
        "share_network_id",
        verbose_name=_("Share Network"),
        link=get_share_network_link)
    share_server_id = tables.Column(
        "share_server_id",
        verbose_name=_("Share Server Id"),
        link=get_share_server_link)
    share_id = tables.Column(
        "share_id",
        verbose_name=_("Share ID"),
        link=get_share_link)

    def get_object_display(self, share_instance):
        return six.text_type(share_instance.id)

    def get_object_id(self, share_instance):
        return six.text_type(share_instance.id)
