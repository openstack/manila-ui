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

from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.admin.defaults import tables as default_tbl


MANILA_QUOTA_NAMES = {
    'shares': _('Shares'),
    'gigabytes': _('Share gigabytes'),
    'snapshots': _('Share snapshots'),
    'snapshot_gigabytes': _('Share snapshot gigabytes'),
    'share_networks': _('Shares Networks'),
}


def get_quota_name(quota):
    return MANILA_QUOTA_NAMES.get(quota.name,
                                  quota.name.replace("_", " ").title())


class UpdateDefaultShareQuotas(default_tbl.UpdateDefaultQuotas):
    name = 'update_share_defaults'
    step = 'update_default_share_quotas'


class ShareQuotasTable(tables.DataTable):
    name = tables.Column(get_quota_name, verbose_name=_('Quota Name'))
    limit = tables.Column("limit", verbose_name=_('Limit'))

    def get_object_id(self, obj):
        return obj.name

    class Meta(object):
        name = "share_quotas"
        verbose_name = _("Shared Quotas")
        table_actions = (default_tbl.QuotaFilterAction,
                         UpdateDefaultShareQuotas)
        multi_select = False
