# Copyright 2017 Mirantis, Inc.
# All rights reserved.
#
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

from django.conf import urls

from manila_ui.dashboards.project.share_group_snapshots import views
from manila_ui import features


if features.is_share_groups_enabled():
    urlpatterns = [
        urls.url(
            r'^$',
            views.ShareGroupSnapshotsView.as_view(),
            name='index'),
        urls.url(
            r'^(?P<share_group_id>[^/]+)/snapshot_create/$',
            views.CreateShareGroupSnapshotView.as_view(),
            name='create'),
        urls.url(
            r'^(?P<share_group_snapshot_id>[^/]+)/$',
            views.ShareGroupSnapshotDetailView.as_view(),
            name='detail'),
        urls.url(
            r'^(?P<share_group_snapshot_id>[^/]+)/update/$',
            views.UpdateShareGroupSnapshotView.as_view(),
            name='update'),
    ]
