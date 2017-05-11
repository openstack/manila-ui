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

from manila_ui.dashboards.admin.share_group_types import views
from manila_ui import features


if features.is_share_groups_enabled():
    urlpatterns = [
        urls.url(
            r'^$',
            views.ShareGroupTypesView.as_view(),
            name='index'),
        urls.url(
            r'^create$',
            views.CreateShareGroupTypeView.as_view(),
            name='create'),
        urls.url(
            r'^(?P<share_group_type_id>[^/]+)/update$',
            views.UpdateShareGroupTypeView.as_view(),
            name='update'),
        urls.url(
            r'^(?P<share_group_type_id>[^/]+)/manage_access$',
            views.ManageShareGroupTypeAccessView.as_view(),
            name='manage_access'),
    ]
