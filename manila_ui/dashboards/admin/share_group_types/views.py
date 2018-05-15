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
Admin views for managing share group types.
"""

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized
from horizon import workflows

from manila_ui.api import manila
from manila_ui.dashboards.admin.share_group_types import forms as sgt_forms
from manila_ui.dashboards.admin.share_group_types import tables as sgt_tables
import manila_ui.dashboards.admin.share_group_types.workflows as sgt_workflows
from manila_ui.dashboards import utils as common_utils


class ShareGroupTypesView(tables.MultiTableView):
    table_classes = (
        sgt_tables.ShareGroupTypesTable,
    )
    template_name = "admin/share_group_types/index.html"
    page_title = _("Share Group Types")

    @memoized.memoized_method
    def get_share_group_types_data(self):
        try:
            share_group_types = manila.share_group_type_list(self.request)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share group types.'))
            return []

        share_types = manila.share_type_list(self.request)
        st_mapping = {}
        for st in share_types:
            st_mapping[st.id] = st.name
        for sgt in share_group_types:
            sgt.group_specs = common_utils.metadata_to_str(
                sgt.group_specs, 8, 45)
            sgt.share_types = ", ".join(
                [st_mapping[st] for st in sgt.share_types])
        return share_group_types


class CreateShareGroupTypeView(forms.ModalFormView):
    form_class = sgt_forms.CreateShareGroupTypeForm
    form_id = "create_share_group_type"
    template_name = 'admin/share_group_types/create.html'
    modal_header = _("Create Share Group Type")
    modal_id = "create_share_group_type_modal"
    submit_label = _("Create")
    submit_url = reverse_lazy("horizon:admin:share_group_types:create")
    success_url = reverse_lazy("horizon:admin:share_group_types:index")
    page_title = _("Create Share Group Type")


class ManageShareGroupTypeAccessView(workflows.WorkflowView):
    workflow_class = sgt_workflows.ManageShareGroupTypeAccessWorkflow
    template_name = "admin/share_group_types/manage_access.html"
    success_url = 'horizon:admin:share_group_types:index'
    page_title = _("Manage Share Group Type Access")

    def get_initial(self):
        return {'id': self.kwargs["share_group_type_id"]}

    def get_context_data(self, **kwargs):
        context = super(ManageShareGroupTypeAccessView, self).get_context_data(
            **kwargs)
        context['id'] = self.kwargs['share_group_type_id']
        return context


class UpdateShareGroupTypeView(forms.ModalFormView):
    form_class = sgt_forms.UpdateShareGroupTypeForm
    form_id = "update_share_group_type"
    template_name = "admin/share_group_types/update.html"
    modal_header = _("Update Share Group Type")
    modal_id = "update_share_group_type_modal"
    submit_label = _("Update")
    submit_url = "horizon:admin:share_group_types:update"
    success_url = reverse_lazy("horizon:admin:share_group_types:index")
    page_title = _("Update Share Group Type")

    def get_object(self):
        if not hasattr(self, "_object"):
            sgt_id = self.kwargs["share_group_type_id"]
            try:
                self._object = manila.share_group_type_get(
                    self.request, sgt_id)
            except Exception:
                msg = _("Unable to retrieve share_gruop_type.")
                url = reverse("horizon:admin:share_group_types:index")
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateShareGroupTypeView, self).get_context_data(
            **kwargs)
        args = (
            self.get_object().id,
        )
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        share_group_type = self.get_object()
        return {
            "id": self.kwargs["share_group_type_id"],
            "name": share_group_type.name,
            "group_specs": share_group_type.group_specs,
        }
