#!/usr/bin/env python

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

#
# Starting with Django 1.7, when a django app is loaded, it is assigned a
# default label containing the portion of the application name after the last
# period, and this name has to be globally unique.  When horizon project
# dashboard, openstack_dashboard.dashboards.project, is loaded, it is assigned
# the label 'project'.  But when the manila dashboard
# manila_ui.dashboards.project is loaded, it label will conflict with
# horizon's.  Therefore this AppConfig class exists merely to specify a unique
# configuration label and avoid this conflict.
#

from django import apps


class Config(apps.AppConfig):
    name = 'manila_ui.dashboards.project'
    label = 'manila_project'
