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
Project views for managing share group snapshots.
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
import manila_ui.dashboards.project.share_group_snapshots.forms as sgs_forms
import manila_ui.dashboards.project.share_group_snapshots.tables as sgs_tables
import manila_ui.dashboards.project.share_group_snapshots.tabs as sgs_tabs


class ShareGroupSnapshotsView(tables.MultiTableView):
    table_classes = (
        sgs_tables.ShareGroupSnapshotsTable,
    )
    template_name = "project/share_group_snapshots/index.html"
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
    template_name = "project/share_group_snapshots/detail.html"
    redirect_url = reverse_lazy("horizon:project:share_group_snapshots:index")

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


class CreateShareGroupSnapshotView(forms.ModalFormView):
    form_class = sgs_forms.CreateShareGroupSnapshotForm
    form_id = "create_share_group_snapshot"
    template_name = 'project/share_group_snapshots/create.html'
    modal_header = _("Create Share Group Snapshot")
    modal_id = "create_share_group_snapshot_modal"
    submit_label = _("Create Share Group Snapshot")
    submit_url = "horizon:project:share_group_snapshots:create"
    success_url = reverse_lazy('horizon:project:share_group_snapshots:index')
    page_title = _('Create Share Group Snapshot')

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        sg_id = self.kwargs['share_group_id']
        try:
            sg = manila.share_group_get(self.request, sg_id)
            context['share_group_name'] = sg.name or sg_id
        except Exception:
            exceptions.handle(
                self.request,
                _("Unable to get the specified share group '%s' for "
                  "snapshot creation.") % sg_id)
            context['share_group_name'] = sg_id
        context['share_group_id'] = sg_id
        # TODO(vponomaryov): add support of quotas when it is implemented
        # for share group snapshots on server side.
        return context

    def get_initial(self):
        self.submit_url = reverse(self.submit_url, kwargs=self.kwargs)
        return {'share_group_id': self.kwargs["share_group_id"]}


class UpdateShareGroupSnapshotView(forms.ModalFormView):
    form_class = sgs_forms.UpdateShareGroupSnapshotForm
    form_id = "update_share_group_snapshot"
    template_name = 'project/share_group_snapshots/update.html'
    modal_header = _("Update Share Group Snapshot")
    modal_id = "update_share_group_snapshot_modal"
    submit_label = _("Update")
    submit_url = "horizon:project:share_group_snapshots:update"
    success_url = reverse_lazy('horizon:project:share_group_snapshots:index')
    page_title = _('Update Share Group')

    @memoized.memoized_method
    def get_object(self):
        if not hasattr(self, "_object"):
            try:
                self._object = manila.share_group_snapshot_get(
                    self.request, self.kwargs['share_group_snapshot_id'])
            except Exception:
                msg = _('Unable to retrieve share group snapshot.')
                url = reverse('horizon:project:share_group_snapshots:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        snapshot = self.get_object()
        return {
            'share_group_snapshot_id': self.kwargs["share_group_snapshot_id"],
            'name': snapshot.name,
            'description': snapshot.description,
        }
