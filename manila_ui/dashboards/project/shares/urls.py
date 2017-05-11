# Copyright 2012 Nebula, Inc.
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

from django.conf import urls

from manila_ui.dashboards.project.shares.replicas import views as replica_views
from manila_ui.dashboards.project.shares import views as shares_views
from manila_ui import features


urlpatterns = [
    urls.url(
        r'^$',
        shares_views.SharesView.as_view(),
        name='index'),
    urls.url(
        r'^create/$',
        shares_views.CreateView.as_view(),
        name='create'),
    urls.url(
        r'^(?P<share_id>[^/]+)/rules/$',
        shares_views.ManageRulesView.as_view(),
        name='manage_rules'),
    urls.url(
        r'^(?P<share_id>[^/]+)/rule_add/$',
        shares_views.AddRuleView.as_view(),
        name='rule_add'),
    urls.url(
        r'^(?P<share_id>[^/]+)/$',
        shares_views.DetailView.as_view(),
        name='detail'),
    urls.url(
        r'^(?P<share_id>[^/]+)/update/$',
        shares_views.UpdateView.as_view(),
        name='update'),
    urls.url(
        r'^(?P<share_id>[^/]+)/update_metadata/$',
        shares_views.UpdateMetadataView.as_view(),
        name='update_metadata'),
    urls.url(
        r'^(?P<share_id>[^/]+)/extend/$',
        shares_views.ExtendView.as_view(),
        name='extend'),
    urls.url(
        r'^(?P<share_id>[^/]+)/revert/$',
        shares_views.RevertView.as_view(),
        name='revert'),
]

if features.is_replication_enabled():
    urlpatterns.extend([
        urls.url(
            r'^(?P<share_id>[^/]+)/create_replica/$',
            replica_views.CreateReplicaView.as_view(),
            name='create_replica'),
        urls.url(
            r'^(?P<share_id>[^/]+)/replicas/$',
            replica_views.ManageReplicasView.as_view(),
            name='manage_replicas'),
        urls.url(
            r'^replica/(?P<replica_id>[^/]+)$',
            replica_views.DetailReplicaView.as_view(),
            name='replica_detail'),
        urls.url(
            r'^replica/(?P<replica_id>[^/]+)/set_replica_as_active$',
            replica_views.SetReplicaAsActiveView.as_view(),
            name='set_replica_as_active'),
    ])
