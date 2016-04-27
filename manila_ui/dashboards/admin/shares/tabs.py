# Copyright 2014 OpenStack Foundation
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

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard.api import base
from openstack_dashboard.api import neutron

from manila_ui.api import manila
from manila_ui.api import network
from manila_ui.dashboards.admin.shares import tables
from manila_ui.dashboards.admin.shares import utils


class SnapshotsTab(tabs.TableTab):
    table_classes = (tables.SnapshotsTable, )
    name = _("Snapshots")
    slug = "snapshots_tab"
    template_name = "horizon/common/_detail_table.html"

    def _set_id_if_nameless(self, snapshots):
        for snap in snapshots:
            if not snap.name:
                snap.name = snap.id

    def get_snapshots_data(self):
        snapshots = []
        try:
            snapshots = manila.share_snapshot_list(
                self.request, search_opts={'all_tenants': True})
            shares = manila.share_list(self.request)
            share_names = dict([(share.id, share.name or share.id)
                                for share in shares])
            for snapshot in snapshots:
                snapshot.share = share_names.get(snapshot.share_id)
        except Exception:
            msg = _("Unable to retrieve snapshot list.")
            exceptions.handle(self.request, msg)

        # Gather our projects to correlate against IDs
        utils.set_project_name_to_objects(self.request, snapshots)

        return snapshots


class SharesTab(tabs.TableTab):
    table_classes = (tables.SharesTable, )
    name = _("Shares")
    slug = "shares_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_shares_data(self):
        shares = []
        try:
            shares = manila.share_list(
                self.request, search_opts={'all_tenants': True})
            snapshots = manila.share_snapshot_list(
                self.request, detailed=True, search_opts={'all_tenants': True})
            share_ids_with_snapshots = []
            for snapshot in snapshots:
                share_ids_with_snapshots.append(snapshot.to_dict()['share_id'])
            for share in shares:
                if share.to_dict()['id'] in share_ids_with_snapshots:
                    setattr(share, 'has_snapshot', True)
                else:
                    setattr(share, 'has_snapshot', False)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share list.'))

        # Gather our projects to correlate against IDs
        utils.set_project_name_to_objects(self.request, shares)

        return shares


class ShareTypesTab(tabs.TableTab):
    table_classes = (tables.ShareTypesTable, )
    name = _("Share Types")
    slug = "share_types_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_share_types_data(self):
        try:
            share_types = manila.share_type_list(self.request)
        except Exception:
            share_types = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share types"))
        # Convert dict with extra specs to friendly view
        for st in share_types:
            es_str = ""
            for k, v in st.extra_specs.iteritems():
                es_str += "%s=%s\r\n<br />" % (k, v)
            st.extra_specs = mark_safe(es_str)
        return share_types


class SecurityServiceTab(tabs.TableTab):
    table_classes = (tables.SecurityServiceTable,)
    name = _("Security Services")
    slug = "security_services_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(
                self.request, search_opts={'all_tenants': True})
        except Exception:
            security_services = []
            exceptions.handle(self.request,
                              _("Unable to retrieve security services"))

        utils.set_project_name_to_objects(self.request, security_services)
        return security_services


class ShareNetworkTab(tabs.TableTab):
    name = _("Share Networks")
    slug = "share_networks_tab"
    template_name = "horizon/common/_detail_table.html"

    def __init__(self, tab_group, request):
        if base.is_service_enabled(request, 'network'):
            self.table_classes = (tables.NeutronShareNetworkTable,)
        else:
            self.table_classes = (tables.NovaShareNetworkTable,)
        super(ShareNetworkTab, self).__init__(tab_group, request)

    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(
                self.request, detailed=True, search_opts={'all_tenants': True})
            if base.is_service_enabled(self.request, 'network'):
                neutron_net_names = dict((net.id, net.name) for net in
                                         neutron.network_list(self.request))
                neutron_subnet_names = dict((net.id, net.name) for net in
                                            neutron.subnet_list(self.request))
                for sn in share_networks:
                    sn.neutron_net = neutron_net_names.get(
                        sn.neutron_net_id) or sn.neutron_net_id or "-"
                    sn.neutron_subnet = neutron_subnet_names.get(
                        sn.neutron_subnet_id) or sn.neutron_subnet_id or "-"
            else:
                nova_net_names = dict(
                    [(net.id, net.label)
                     for net in network.network_list(self.request)])
                for sn in share_networks:
                    sn.nova_net = nova_net_names.get(
                        sn.nova_net_id) or sn.nova_net_id or "-"
        except Exception:
            share_networks = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share networks"))
        utils.set_project_name_to_objects(self.request, share_networks)
        return share_networks


class ShareInstancesTab(tabs.TableTab):
    table_classes = (tables.ShareInstancesTable,)
    name = _("Share Instances")
    slug = "share_instances_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_share_instances_data(self):
        try:
            share_instances = manila.share_instance_list(self.request)
        except Exception:
            share_instances = []
            exceptions.handle(
                self.request, _("Unable to retrieve share instances."))
        return share_instances


class ShareInstanceOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("admin/shares/_detail_share_instance.html")

    def get_context_data(self, request):
        return {"share_instance": self.tab_group.kwargs['share_instance']}


class ShareInstanceDetailTabs(tabs.TabGroup):
    slug = "share_instance_details"
    tabs = (ShareInstanceOverviewTab,)


class ShareServerTab(tabs.TableTab):
    table_classes = (tables.ShareServerTable,)
    name = _("Share Servers")
    slug = "share_servers_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_share_servers_data(self):
        try:
            share_servers = manila.share_server_list(
                self.request)
        except Exception:
            share_servers = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share servers"))
        utils.set_project_name_to_objects(self.request, share_servers)
        return share_servers


class ShareServerOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("admin/shares/_detail_share_server.html")

    def get_context_data(self, request):
        return {"share_server": self.tab_group.kwargs['share_server']}


class ShareServerDetailTabs(tabs.TabGroup):
    slug = "share_server_details"
    tabs = (ShareServerOverviewTab,)


class ShareTabs(tabs.TabGroup):
    slug = "share_tabs"
    tabs = (SharesTab, SnapshotsTab, ShareNetworkTab, SecurityServiceTab,
            ShareTypesTab, ShareServerTab, ShareInstancesTab)
    sticky = True


class SnapshotOverviewTab(tabs.Tab):
    name = _("Snapshot Overview")
    slug = "snapshot_overview_tab"
    template_name = ("admin/shares/"
                     "_snapshot_detail_overview.html")

    def get_context_data(self, request):
        return {"snapshot": self.tab_group.kwargs['snapshot']}


class SnapshotDetailTabs(tabs.TabGroup):
    slug = "snapshot_details"
    tabs = (SnapshotOverviewTab,)
