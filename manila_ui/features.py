# Copyright 2017 Mirantis Inc.
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

"""
This module stores functions that return boolean values and say
which manila features are enabled and which are disabled among those
that are optional for manila UI.
These functions are required mostly for complex features, which consist
of more than one logical part in manila UI and requires appropriate logic
change in more than 1 place. For example, to disable share groups feature
we need to do following:
- Remove 'share_groups' panel from 'share groups' panel group in each
  dashboard.
- Disable or do not register URLs for disabled features, so, no one
  will be able to request disabled features knowing direct URL.
- Add/remove buttons for other (not disabled) features that are related
  to it somehow.
"""

from django.conf import settings
from horizon.utils import memoized


@memoized.memoized
def is_share_groups_enabled():
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    return manila_config.get('enable_share_groups', True)


@memoized.memoized
def is_replication_enabled():
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    return manila_config.get('enable_replication', True)


@memoized.memoized
def is_migration_enabled():
    manila_config = getattr(settings, 'OPENSTACK_MANILA_FEATURES', {})
    return manila_config.get('enable_migration', True)
