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

from manila_ui.dashboards.project.share_networks import views


urlpatterns = [
    re_path(
        r'^$',
        views.ShareNetworksView.as_view(),
        name='index'),
    re_path(
        r'^create_share_network$',
        views.Create.as_view(),
        name='share_network_create'),
    re_path(
        r'^(?P<share_network_id>[^/]+)/update$',
        views.Update.as_view(),
        name='share_network_update'),
    re_path(
        r'^(?P<share_network_id>[^/]+)$',
        views.Detail.as_view(),
        name='share_network_detail'),
]
