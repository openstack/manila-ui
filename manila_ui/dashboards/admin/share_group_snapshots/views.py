# Copyright 2017 Mirantis, Inc.
# All rights reserved.
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
Admin views for managing share group snapshots.
"""

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from manila_ui.api import manila
import manila_ui.dashboards.admin.share_group_snapshots.forms as sgs_forms
import manila_ui.dashboards.admin.share_group_snapshots.tables as sgs_tables
import manila_ui.dashboards.admin.share_group_snapshots.tabs as sgs_tabs


class ShareGroupSnapshotsView(tables.MultiTableView):
    table_classes = (
        sgs_tables.ShareGroupSnapshotsTable,
    )
    template_name = "admin/share_group_snapshots/index.html"
    page_title = _("Share Group Snapshots")

    @memoized.memoized_method
    def get_share_group_snapshots_data(self):
        share_group_snapshots = []
        try:
            share_group_snapshots = manila.share_group_snapshot_list(
                self.request, search_opts={'all_tenants': True})
            share_groups = manila.share_group_list(self.request)
            sg_names = dict([(sg.id, sg.name or sg.id) for sg in share_groups])
            for snapshot in share_group_snapshots:
                snapshot.share_group = sg_names.get(snapshot.share_group_id)
        except Exception:
            msg = _("Unable to retrieve share group snapshot list.")
            exceptions.handle(self.request, msg)
        return share_group_snapshots


class ShareGroupSnapshotDetailView(tabs.TabView):
    tab_group_class = sgs_tabs.ShareGroupSnapshotDetailTabs
    template_name = "admin/share_group_snapshots/detail.html"
    redirect_url = reverse_lazy("horizon:admin:share_group_snapshots:index")

    def get_context_data(self, **kwargs):
        context = super(ShareGroupSnapshotDetailView, self).get_context_data(
            **kwargs)
        snapshot = self.get_data()
        snapshot_display_name = snapshot.name or snapshot.id
        context["snapshot"] = snapshot
        context["snapshot_display_name"] = snapshot_display_name
        context["page_title"] = _(
            "Share Group Snapshot Details: %(sgs_display_name)s") % (
            {'sgs_display_name': snapshot_display_name})
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_group_snapshot = manila.share_group_snapshot_get(
                self.request, self.kwargs['share_group_snapshot_id'])
            sg = manila.share_group_get(
                self.request, share_group_snapshot.share_group_id)
            share_group_snapshot.sg_name_or_id = sg.name or sg.id
        except Exception:
            exceptions.handle(
                self.request,
                _('Unable to retrieve share group snapshot details.'),
                redirect=self.redirect_url)
        return share_group_snapshot

    def get_tabs(self, request, *args, **kwargs):
        return self.tab_group_class(
            request, share_group_snapshot=self.get_data(), **kwargs)


class ResetShareGroupSnapshotStatusView(forms.ModalFormView):
    form_class = sgs_forms.ResetShareGroupSnapshotStatusForm
    form_id = "reset_share_group_snapshot_status"
    template_name = 'admin/share_group_snapshots/reset_status.html'
    modal_header = _("Reset Status")
    modal_id = "reset_share_group_snapshot_status_modal"
    submit_label = _("Reset status")
    submit_url = "horizon:admin:share_group_snapshots:reset_status"
    success_url = reverse_lazy("horizon:admin:share_group_snapshots:index")
    page_title = _("Reset Share Group Snapshot Status")

    def get_object(self):
        if not hasattr(self, "_object"):
            s_id = self.kwargs["share_group_snapshot_id"]
            try:
                self._object = manila.share_group_snapshot_get(
                    self.request, s_id)
            except Exception:
                msg = _("Unable to retrieve share group snapshot '%s'.") % s_id
                url = reverse('horizon:admin:share_group_snapshots:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        sgs = self.get_object()
        context['share_group_snapshot_id'] = self.kwargs[
            'share_group_snapshot_id']
        context['share_group_snapshot_name'] = sgs.name or sgs.id
        context['share_group_snapshot_status'] = sgs.status
        context['share_group_id'] = sgs.share_group_id
        context['submit_url'] = reverse(
            self.submit_url, args=(context['share_group_snapshot_id'], ))
        return context

    def get_initial(self):
        sgs = self.get_object()
        return {
            "share_group_snapshot_id": self.kwargs["share_group_snapshot_id"],
            "share_group_snapshot_name": sgs.name or sgs.id,
            "share_group_snapshot_status": sgs.status,
            "share_group_id": sgs.share_group_id,
        }
