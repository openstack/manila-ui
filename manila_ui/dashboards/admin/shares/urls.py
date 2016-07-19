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

from django.conf.urls import url  # noqa

from manila_ui.api import manila
from manila_ui.dashboards.admin.shares.replicas import views as replica_views
from manila_ui.dashboards.admin.shares import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<share_id>[^/]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^snapshots/(?P<snapshot_id>[^/]+)$',
        views.SnapshotDetailView.as_view(),
        name='snapshot-detail'),
    url(r'^share_networks/(?P<share_network_id>[^/]+)$',
        views.ShareNetworkDetailView.as_view(),
        name='share_network_detail'),
    url(r'^security_services/(?P<sec_service_id>[^/]+)$',
        views.SecurityServiceDetailView.as_view(),
        name='security_service_detail'),
    url(r'^create_type$', views.CreateShareTypeView.as_view(),
        name='create_type'),
    url(r'^manage_share_type_access/(?P<share_type_id>[^/]+)$',
        views.ManageShareTypeAccessView.as_view(),
        name='manage_share_type_access'),
    url(r'^update_type/(?P<share_type_id>[^/]+)/extra_specs$',
        views.UpdateShareTypeView.as_view(),
        name='update_type'),
    url(r'^share_servers/(?P<share_server_id>[^/]+)$',
        views.ShareServDetail.as_view(),
        name='share_server_detail'),
    url(r'^\?tab=share_tabs__share_servers_tab$', views.IndexView.as_view(),
        name='share_servers_tab'),
    url(r'^share_instances/(?P<share_instance_id>[^/]+)$',
        views.ShareInstanceDetailView.as_view(),
        name='share_instance_detail'),
    url(r'^\?tab=share_tabs__share_instances_tab$', views.IndexView.as_view(),
        name='share_instances_tab'),
    url(r'^manage$', views.ManageShareView.as_view(), name='manage'),
    url(r'^unmanage/(?P<share_id>[^/]+)$', views.UnmanageShareView.as_view(),
        name='unmanage'),
]

if manila.is_replication_enabled():
    urlpatterns.extend([
        url(r'^(?P<share_id>[^/]+)/replicas/$',
            replica_views.ManageReplicasView.as_view(),
            name='manage_replicas'),
        url(r'^replica/(?P<replica_id>[^/]+)$',
            replica_views.DetailReplicaView.as_view(),
            name='replica_detail'),
        url(r'^replica/(?P<replica_id>[^/]+)/resync_replica$',
            replica_views.ResyncReplicaView.as_view(),
            name='resync_replica'),
        url(r'^replica/(?P<replica_id>[^/]+)/reset_replica_status$',
            replica_views.ResetReplicaStatusView.as_view(),
            name='reset_replica_status'),
        url(r'^replica/(?P<replica_id>[^/]+)/reset_replica_state$',
            replica_views.ResetReplicaStateView.as_view(),
            name='reset_replica_state'),
    ])

if manila.is_migration_enabled():
    urlpatterns.extend([
        url(r'^migration_start/(?P<share_id>[^/]+)$',
            views.MigrationStartView.as_view(), name='migration_start'),
        url(r'^migration_complete/(?P<share_id>[^/]+)$',
            views.MigrationCompleteView.as_view(), name='migration_complete'),
        url(r'^migration_cancel/(?P<share_id>[^/]+)$',
            views.MigrationCancelView.as_view(), name='migration_cancel'),
        url(r'^migration_get_progress/(?P<share_id>[^/]+)$',
            views.MigrationGetProgressView.as_view(),
            name='migration_get_progress'),
    ])
