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

from django.urls import re_path

from manila_ui.dashboards.admin.shares.replicas import views as replica_views
from manila_ui.dashboards.admin.shares import views
from manila_ui import features


urlpatterns = [
    re_path(
        r'^$',
        views.SharesView.as_view(),
        name='index'),
    re_path(
        r'^(?P<share_id>[^/]+)/$',
        views.DetailView.as_view(),
        name='detail'),
    re_path(
        r'^manage$',
        views.ManageShareView.as_view(),
        name='manage'),
    re_path(
        r'^unmanage/(?P<share_id>[^/]+)$',
        views.UnmanageShareView.as_view(),
        name='unmanage'),
]

if features.is_replication_enabled():
    urlpatterns.extend([
        re_path(
            r'^(?P<share_id>[^/]+)/replicas/$',
            replica_views.ManageReplicasView.as_view(),
            name='manage_replicas'),
        re_path(
            r'^replica/(?P<replica_id>[^/]+)$',
            replica_views.DetailReplicaView.as_view(),
            name='replica_detail'),
        re_path(
            r'^replica/(?P<replica_id>[^/]+)/resync_replica$',
            replica_views.ResyncReplicaView.as_view(),
            name='resync_replica'),
        re_path(
            r'^replica/(?P<replica_id>[^/]+)/reset_replica_status$',
            replica_views.ResetReplicaStatusView.as_view(),
            name='reset_replica_status'),
        re_path(
            r'^replica/(?P<replica_id>[^/]+)/reset_replica_state$',
            replica_views.ResetReplicaStateView.as_view(),
            name='reset_replica_state'),
    ])

if features.is_migration_enabled():
    urlpatterns.extend([
        re_path(
            r'^migration_start/(?P<share_id>[^/]+)$',
            views.MigrationStartView.as_view(),
            name='migration_start'),
        re_path(
            r'^migration_complete/(?P<share_id>[^/]+)$',
            views.MigrationCompleteView.as_view(),
            name='migration_complete'),
        re_path(
            r'^migration_cancel/(?P<share_id>[^/]+)$',
            views.MigrationCancelView.as_view(),
            name='migration_cancel'),
        re_path(
            r'^migration_get_progress/(?P<share_id>[^/]+)$',
            views.MigrationGetProgressView.as_view(),
            name='migration_get_progress'),
    ])
