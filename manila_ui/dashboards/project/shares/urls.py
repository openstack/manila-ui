# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from manila_ui.dashboards.project.shares.security_services \
    import views as security_services_views
from manila_ui.dashboards.project.shares.share_networks \
    import views as share_networks_views
from manila_ui.dashboards.project.shares.shares \
    import views as shares_views
from manila_ui.dashboards.project.shares.snapshots\
    import views as snapshot_views
from manila_ui.dashboards.project.shares import views


urlpatterns = patterns(
    'openstack_dashboard.dashboards.project.shares.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', shares_views.CreateView.as_view(), name='create'),
    url(r'^create_security_service$',
        security_services_views.CreateView.as_view(),
        name='create_security_service'),
    url(r'^create_share_network$',
        share_networks_views.Create.as_view(),
        name='create_share_network'),
    url(r'^share_networks/(?P<share_network_id>[^/]+)/update$',
        share_networks_views.Update.as_view(),
        name='update_share_network'),
    url(r'^share_networks/(?P<share_network_id>[^/]+)$',
        share_networks_views.Detail.as_view(),
        name='share_network_detail'),
    url(r'^security_services/(?P<sec_service_id>[^/]+)/update/$',
        security_services_views.UpdateView.as_view(),
        name='update_security_service'),
    url(r'^security_services/(?P<sec_service_id>[^/]+)$',
        security_services_views.Detail.as_view(),
        name='security_service_detail'),
    url(r'^snapshots/(?P<snapshot_id>[^/]+)$',
        snapshot_views.SnapshotDetailView.as_view(),
        name='snapshot-detail'),
    url(r'^(?P<share_id>[^/]+)/create_snapshot/$',
        snapshot_views.CreateSnapshotView.as_view(),
        name='create_snapshot'),
    url(r'^(?P<snapshot_id>[^/]+)/edit_snapshot/$',
        snapshot_views.UpdateView.as_view(),
        name='edit_snapshot'),
    url(r'^(?P<share_id>[^/]+)/rules/$',
        shares_views.ManageRulesView.as_view(),
        name='manage_rules'),
    url(r'^(?P<share_id>[^/]+)/rule_add/$',
        shares_views.AddRuleView.as_view(),
        name='rule_add'),
    url(r'^(?P<share_id>[^/]+)/$',
        shares_views.DetailView.as_view(),
        name='detail'),
    url(r'^(?P<share_id>[^/]+)/update/$',
        shares_views.UpdateView.as_view(),
        name='update'),
    url(r'^(?P<share_id>[^/]+)/update_metadata/$',
        shares_views.UpdateMetadataView.as_view(),
        name='update_metadata'),
    url(r'^(?P<share_id>[^/]+)/extend/$',
        shares_views.ExtendView.as_view(),
        name='extend'),
)
