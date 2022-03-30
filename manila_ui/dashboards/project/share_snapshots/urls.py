# Copyright 2017 Mirantis, Inc.
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

from django.urls import re_path

from manila_ui.dashboards.project.share_snapshots import views


urlpatterns = [
    re_path(
        r'^$',
        views.ShareSnapshotsView.as_view(),
        name='index'),
    re_path(
        r'^(?P<share_id>[^/]+)/share_snapshot_create/$',
        views.CreateShareSnapshotView.as_view(),
        name='share_snapshot_create'),
    re_path(
        r'^(?P<snapshot_id>[^/]+)/share_snapshot_edit/$',
        views.UpdateShareSnapshotView.as_view(),
        name='share_snapshot_edit'),
    re_path(
        r'^(?P<snapshot_id>[^/]+)$',
        views.ShareSnapshotDetailView.as_view(),
        name='share_snapshot_detail'),
    re_path(
        r'^(?P<snapshot_id>[^/]+)/share_snapshot_rules/$',
        views.ManageShareSnapshotRulesView.as_view(),
        name='share_snapshot_manage_rules'),
    re_path(
        r'^(?P<snapshot_id>[^/]+)/share_snapshot_rule_add/$',
        views.AddShareSnapshotRuleView.as_view(),
        name='share_snapshot_rule_add'),
]
