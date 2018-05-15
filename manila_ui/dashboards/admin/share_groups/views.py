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
Admin views for managing share groups.
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
from manila_ui.dashboards.admin.share_groups import forms as sg_forms
from manila_ui.dashboards.admin.share_groups import tables as sg_tables
from manila_ui.dashboards.admin.share_groups import tabs as sg_tabs


class ShareGroupsView(tables.MultiTableView):
    table_classes = (
        sg_tables.ShareGroupsTable,
    )
    template_name = "admin/share_groups/index.html"
    page_title = _("Share Groups")

    @memoized.memoized_method
    def get_share_groups_data(self):
        try:
            share_groups = manila.share_group_list(
                self.request, detailed=True)
        except Exception:
            share_groups = []
            exceptions.handle(
                self.request, _("Unable to retrieve share groups."))
        return share_groups


class ShareGroupDetailView(tabs.TabView):
    tab_group_class = sg_tabs.ShareGroupDetailTabs
    template_name = 'admin/share_groups/detail.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        share_group = self.get_data()
        context["share_group"] = share_group
        context["page_title"] = (
            _("Share Group Details: %s") % share_group.id)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_group_id = self.kwargs['share_group_id']
            share_group = manila.share_group_get(self.request, share_group_id)
            members = manila.share_list(
                self.request, search_opts={"share_group_id": share_group_id})
            share_group.members = members
            share_types = manila.share_type_list(self.request)
            share_group.share_types = [
                {"id": st.id,
                 "name": st.name,
                 "is_public": getattr(st, 'share_type_access:is_public'),
                 "dhss": st.extra_specs.get('driver_handles_share_servers')}
                for st in share_types if st.id in share_group.share_types
            ]
            return share_group
        except Exception:
            redirect = reverse('horizon:admin:share_groups:index')
            exceptions.handle(
                self.request,
                _('Unable to retrieve share group details.'),
                redirect=redirect)

    def get_tabs(self, request, *args, **kwargs):
        share_group = self.get_data()
        return self.tab_group_class(request, share_group=share_group, **kwargs)


class ResetShareGroupStatusView(forms.ModalFormView):
    form_class = sg_forms.ResetShareGroupStatusForm
    form_id = "reset_share_group_status"
    template_name = 'admin/share_groups/reset_status.html'
    modal_header = _("Reset Status")
    modal_id = "reset_share_group_status_modal"
    submit_label = _("Reset status")
    submit_url = "horizon:admin:share_groups:reset_status"
    success_url = reverse_lazy("horizon:admin:share_groups:index")
    page_title = _("Reset Share Group Status")

    def get_object(self):
        if not hasattr(self, "_object"):
            sg_id = self.kwargs["share_group_id"]
            try:
                self._object = manila.share_group_get(self.request, sg_id)
            except Exception:
                msg = _("Unable to retrieve share group '%s'.") % sg_id
                url = reverse('horizon:admin:share_groups:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        sg = self.get_object()
        context['share_group_id'] = self.kwargs['share_group_id']
        context['share_group_name'] = sg.name or sg.id
        context['share_group_status'] = sg.status
        context['submit_url'] = reverse(
            self.submit_url, args=(context['share_group_id'], ))
        return context

    def get_initial(self):
        sg = self.get_object()
        return {
            "share_group_id": self.kwargs["share_group_id"],
            "share_group_name": sg.name or sg.id,
            "share_group_status": sg.status,
        }
