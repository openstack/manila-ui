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

from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import tabs
from openstack_dashboard.api import keystone

from manila_ui.api import manila
from manila_ui.dashboards.project.resource_locks import tables as lock_tables


class LockDataMixin(object):
    is_admin = False

    def _get_common_data(self, resource_type):
        request = self.request
        try:
            all_locks = self.tab_group.get_all_locks()
            filtered_locks = [
                lock for lock in all_locks
                if resource_type in (
                    getattr(lock, 'resource_level', '').lower(),
                    getattr(lock, 'resource_type', '').lower())
            ]
            if not filtered_locks:
                return []
            share_opts = {'all_tenants': True} if self.is_admin else {}
            shares = manila.share_list(request, search_opts=share_opts)
            share_map = {s.id: s.name or s.id for s in shares}
            user_map = {request.user.id: request.user.username}
            try:
                users = keystone.user_list(request)
                user_map.update({u.id: u.name for u in users})
            except Exception:
                pass
            if resource_type == 'share':
                for lock in filtered_locks:
                    if not getattr(lock, 'resource_name', None):
                        lock.resource_name = share_map.get(
                            lock.resource_id, lock.resource_id)
                    lock.user_name = user_map.get(lock.user_id, lock.user_id)
                return filtered_locks
            if resource_type == 'access_rule':
                parent_ids = {
                    getattr(lock, 'parent_resource_id', None)
                    for lock in filtered_locks
                } - {None}
                access_val_map = {}
                parent_map = {}
                for share_id in parent_ids:
                    try:
                        rules = manila.share_rules_list(request, share_id)
                        for rule in rules:
                            access_val_map[rule.id] = getattr(
                                rule, 'access_to', rule.id)
                            parent_map[rule.id] = share_id
                    except Exception:
                        pass
                for lock in filtered_locks:
                    r_id = lock.resource_id
                    if r_id not in access_val_map:
                        try:
                            rule = manila.share_rule_get(request, r_id)
                            access_val_map[r_id] = getattr(
                                rule, 'access_to', r_id)
                            parent_map[r_id] = getattr(
                                rule, 'share_id', None)
                        except Exception:
                            access_val_map[r_id] = getattr(
                                lock, 'resource_name', r_id)
                for lock in filtered_locks:
                    r_id = lock.resource_id
                    lock.access_to = access_val_map.get(r_id, r_id)
                    p_id = (getattr(lock, 'parent_resource_id', None) or
                            parent_map.get(r_id))
                    lock.parent_resource_id = p_id
                    lock.parent_resource_name = (
                        share_map.get(p_id, p_id) if p_id
                        else _("Unknown Share"))
                    lock.user_name = user_map.get(lock.user_id, lock.user_id)
                    lock.resource_action = getattr(
                        lock, 'resource_action', '')
                return filtered_locks
        except Exception:
            msg = _("Unable to retrieve %s locks.") % resource_type
            exceptions.handle(request, msg)
            return []


class SharesTab(tabs.TableTab, LockDataMixin):
    name = _("Shares")
    slug = "shares_tab"
    table_classes = (lock_tables.SharesLockTable,)
    template_name = "horizon/common/_detail_table.html"

    def get_shares_locks_data(self):
        return self._get_common_data('share')


class AccessRulesTab(tabs.TableTab, LockDataMixin):
    name = _("Access Rules")
    slug = "rules_tab"
    table_classes = (lock_tables.AccessRulesLockTable,)
    template_name = "horizon/common/_detail_table.html"

    def get_rules_locks_data(self):
        return self._get_common_data('access_rule')


class ResourceLockTabs(tabs.TabGroup):
    slug = "resource_lock_tabs"
    tabs = (SharesTab, AccessRulesTab)
    sticky = False

    def get_all_locks(self):
        if not hasattr(self, "_all_locks"):
            is_admin_context = self.kwargs.get('is_admin') or any(
                getattr(t, 'is_admin', False) for t in self.get_tabs()
            )
            search_opts = {'all_projects': True} if is_admin_context else {}
            self._all_locks = manila.resource_lock_list(
                self.request, search_opts=search_opts)
        return self._all_locks
