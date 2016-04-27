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

import six

from django.core.urlresolvers import reverse
from django.template.defaultfilters import title  # noqa
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from manila_ui.api import manila
from manila_ui.dashboards.project.shares.share_networks \
    import tables as share_networks_tables
from manila_ui.dashboards.project.shares.shares import tables as shares_tables
from manila_ui.dashboards.project.shares.snapshots \
    import tables as snapshot_tables


def get_size(share):
    return _("%sGiB") % share.size


class CreateShareType(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share Type")
    url = "horizon:admin:shares:create_type"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share_extension:types_manage"),)


class DeleteShareType(tables.DeleteAction):
    data_type_singular = _("Share Type")
    data_type_plural = _("Share Types")
    policy_rules = (("share", "share_extension:types_manage"),)

    def delete(self, request, obj_id):
        manila.share_type_delete(request, obj_id)


class ManageShareTypeAccess(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Share Type Access")
    url = "horizon:admin:shares:manage_share_type_access"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share_extension:share_type_access"),)

    def allowed(self, request, obj_id):
        st = manila.share_type_get(request, obj_id)
        # Enable it only for private share types
        return not st.is_public

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class ManageShareAction(tables.LinkAction):
    name = "manage"
    verbose_name = _("Manage Share")
    url = "horizon:admin:shares:manage"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("share", "share_extension:share_manage"),)
    ajax = True


class UnmanageShareAction(tables.LinkAction):
    name = "unmanage"
    verbose_name = _("Unmanage Share")
    url = "horizon:admin:shares:unmanage"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = (("share", "share_extension:share_unmanage"),)

    def allowed(self, request, share=None):
        if (not share or share.share_server_id or
                share.status.upper() not in shares_tables.DELETABLE_STATES):
            return False
        elif hasattr(share, 'has_snapshot'):
            return not share.has_snapshot
        return False


class UpdateShareType(tables.LinkAction):
    name = "update share type"
    verbose_name = _("Update Share Type")
    url = "horizon:admin:shares:update_type"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share_extension:types_manage"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}


class ShareTypesFilterAction(tables.FilterAction):

    def filter(self, table, share_types, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [st for st in share_types if q in st.name.lower()]


class ShareTypesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"))
    extra_specs = tables.Column("extra_specs", verbose_name=_("Extra specs"), )
    visibility = tables.Column(
        "is_public", verbose_name=_("Visibility"),
        filters=(lambda d: 'public' if d is True else 'private', ),)

    def get_object_display(self, share_type):
        return share_type.name

    def get_object_id(self, share_type):
        return str(share_type.id)

    class Meta(object):
        name = "share_types"
        verbose_name = _("Share Types")
        table_actions = (CreateShareType, DeleteShareType,
                         ShareTypesFilterAction, )
        row_actions = (
            UpdateShareType, DeleteShareType,
            ManageShareTypeAccess,
        )


class SharesFilterAction(tables.FilterAction):

    def filter(self, table, shares, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [share for share in shares
                if q in share.name.lower()]


class SharesTable(shares_tables.SharesTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:shares:detail")
    host = tables.Column("host", verbose_name=_("Host"))
    project = tables.Column("project_name", verbose_name=_("Project"))

    def get_share_server_link(share):
        if getattr(share, 'share_server_id', None):
            return reverse("horizon:admin:shares:share_server_detail",
                           args=(share.share_server_id,))
        else:
            return None

    share_server = tables.Column("share_server_id",
                                 verbose_name=_("Share Server"),
                                 link=get_share_server_link)

    class Meta(object):
        name = "shares"
        verbose_name = _("Shares")
        status_columns = ["status"]
        row_class = shares_tables.UpdateRow
        table_actions = (
            shares_tables.DeleteShare,
            ManageShareAction,
            SharesFilterAction,
        )
        row_actions = (
            shares_tables.DeleteShare,
            UnmanageShareAction,
        )
        columns = (
            'tenant', 'host', 'name', 'size', 'status', 'visibility',
            'share_type', 'protocol', 'share_server',
        )


class SnapshotShareNameColumn(tables.Column):
    def get_link_url(self, snapshot):
        return reverse(self.link, args=(snapshot.share_id,))


class DeleteSnapshot(tables.DeleteAction):
    data_type_singular = _("Snapshot")
    data_type_plural = _("Snapshots")
    action_past = _("Scheduled deletion of %(data_type)s")
    policy_rules = (("snapshot", "snapshot:delete"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "project_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        name = self.table.get_object_display(obj)
        try:
            manila.share_snapshot_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete snapshot "%s". One or more shares '
                    'depend on it.')
            exceptions.check_message(["snapshots", "dependent"], msg % name)
            raise

    def allowed(self, request, snapshot=None):
        if snapshot:
            return snapshot.status.upper() in shares_tables.DELETABLE_STATES
        return True


class SnapshotsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("in-use", True),
        ("available", True),
        ("creating", None),
        ("error", False),
    )
    STATUS_DISPLAY_CHOICES = (
        ("in-use", pgettext_lazy("Current status of snapshot", u"In-use")),
        ("available", pgettext_lazy("Current status of snapshot",
                                    u"Available")),
        ("creating", pgettext_lazy("Current status of snapshot", u"Creating")),
        ("error", pgettext_lazy("Current status of snapshot", u"Error")),
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:shares:snapshot-detail")
    description = tables.Column("description",
                                verbose_name=_("Description"),
                                truncate=40)
    size = tables.Column(get_size,
                         verbose_name=_("Size"),
                         attrs={'data-type': 'size'})
    status = tables.Column("status",
                           filters=(title,),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES,
                           display_choices=STATUS_DISPLAY_CHOICES)
    source = SnapshotShareNameColumn("share",
                                     verbose_name=_("Source"),
                                     link="horizon:admin:shares:detail")

    def get_object_display(self, obj):
        return obj.name

    class Meta(object):
        name = "snapshots"
        verbose_name = _("Snapshots")
        status_columns = ["status"]
        row_class = snapshot_tables.UpdateRow
        table_actions = (DeleteSnapshot, )
        row_actions = (DeleteSnapshot, )


class DeleteSecurityService(tables.DeleteAction):
    data_type_singular = _("Security Service")
    data_type_plural = _("Security Services")
    policy_rules = (("share", "security_service:delete"),)

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class DeleteShareServer(tables.DeleteAction):
    data_type_singular = _("Share Server")
    data_type_plural = _("Share Server")
    policy_rules = (("share", "share_server:delete"),)

    def delete(self, request, obj_id):
        manila.share_server_delete(request, obj_id)

    def allowed(self, request, share_serv):
        if share_serv:
            share_search_opts = {'share_server_id': share_serv.id}
            shares_list = manila.share_list(request,
                                            search_opts=share_search_opts)
            if shares_list:
                return False
            return share_serv.status not in ["deleting", "creating"]
        return True


class SecurityServiceTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:shares:security_service_detail")
    project = tables.Column("project_name", verbose_name=_("Project"))
    dns_ip = tables.Column("dns_ip", verbose_name=_("DNS IP"))
    server = tables.Column("server", verbose_name=_("Server"))
    domain = tables.Column("domain", verbose_name=_("Domain"))
    user = tables.Column("user", verbose_name=_("Sid"))

    def get_object_display(self, security_service):
        return security_service.name

    def get_object_id(self, security_service):
        return str(security_service.id)

    class Meta(object):
        name = "security_services"
        verbose_name = _("Security Services")
        table_actions = (DeleteSecurityService,)
        row_actions = (DeleteSecurityService,)


class UpdateShareServerRow(tables.Row):
    ajax = True

    def get_data(self, request, share_serv_id):
        share_serv = manila.share_server_get(request, share_serv_id)
        return share_serv


class NovaShareNetworkTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:shares:share_network_detail")
    project = tables.Column("project_name", verbose_name=_("Project"))
    nova_net = tables.Column("nova_net", verbose_name=_("Nova Net"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column("network_type",
                                 verbose_name=_("Network Type"))
    segmentation_id = tables.Column("segmentation_id",
                                    verbose_name=_("Segmentation Id"))

    def get_object_display(self, share_network):
        return share_network.name or str(share_network.id)

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta(object):
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (share_networks_tables.Delete, )
        row_class = share_networks_tables.UpdateRow
        row_actions = (share_networks_tables.Delete, )


class NeutronShareNetworkTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
                         link="horizon:project:shares:share_network_detail")
    project = tables.Column("project_name", verbose_name=_("Project"))
    neutron_net = tables.Column("neutron_net", verbose_name=_("Neutron Net"))
    neutron_subnet = tables.Column(
        "neutron_subnet", verbose_name=_("Neutron Subnet"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column("network_type",
                                 verbose_name=_("Network Type"))
    segmentation_id = tables.Column("segmentation_id",
                                    verbose_name=_("Segmentation Id"))

    def get_object_display(self, share_network):
        return share_network.name or str(share_network.id)

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta(object):
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (share_networks_tables.Delete, )
        row_class = share_networks_tables.UpdateRow
        row_actions = (share_networks_tables.Delete, )


class SharesServersFilterAction(tables.FilterAction):

    def filter(self, table, shares, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [share for share in shares
                if q in share.name.lower()]


class ShareServerTable(tables.DataTable):
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
    uid = tables.Column("id", verbose_name=_("Id"),
                        link="horizon:admin:shares:share_server_detail")
    host = tables.Column("host", verbose_name=_("Host"))
    project = tables.Column("project_name", verbose_name=_("Project"))

    def get_share_server_link(share_serv):
        if hasattr(share_serv, 'share_network_id'):
            return reverse("horizon:admin:shares:share_network_detail",
                           args=(share_serv.share_network_id,))
        else:
            return None

    share_net_name = tables.Column("share_network_name",
                                   verbose_name=_("Share Network"),
                                   link=get_share_server_link)
    status = tables.Column("status", verbose_name=_("Status"),
                           status=True, filters=(title,),
                           status_choices=STATUS_CHOICES,
                           display_choices=STATUS_DISPLAY_CHOICES)

    def get_object_display(self, share_server):
        return six.text_type(share_server.id)

    def get_object_id(self, share_server):
        return six.text_type(share_server.id)

    class Meta(object):
        name = "share_servers"
        status_columns = ["status"]
        verbose_name = _("Share Server")
        table_actions = (DeleteShareServer, SharesServersFilterAction)
        row_class = UpdateShareServerRow
        row_actions = (DeleteShareServer, )


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
        link="horizon:admin:shares:share_instance_detail")
    host = tables.Column("host", verbose_name=_("Host"))
    status = tables.Column("status",
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
        table_actions = (shares_tables.SharesFilterAction, )
        multi_select = False

    def get_share_network_link(share_instance):
        if getattr(share_instance, 'share_network_id', None):
            return reverse("horizon:admin:shares:share_network_detail",
                           args=(share_instance.share_network_id,))
        else:
            return None

    def get_share_server_link(share_instance):
        if getattr(share_instance, 'share_server_id', None):
            return reverse("horizon:admin:shares:share_server_detail",
                           args=(share_instance.share_server_id,))
        else:
            return None

    def get_share_link(share_instance):
        if getattr(share_instance, 'share_id', None):
            return reverse("horizon:project:shares:detail",
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
