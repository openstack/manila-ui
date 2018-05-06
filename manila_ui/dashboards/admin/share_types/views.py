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
Admin views for managing share types.
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
from manila_ui.dashboards.admin.share_types import forms as project_forms
from manila_ui.dashboards.admin.share_types import tables as st_tables
import manila_ui.dashboards.admin.share_types.workflows as st_workflows
from manila_ui.dashboards import utils as common_utils


class ShareTypesView(tables.MultiTableView):
    table_classes = (
        st_tables.ShareTypesTable,
    )
    template_name = "admin/share_types/index.html"
    page_title = _("Share Types")

    @memoized.memoized_method
    def get_share_types_data(self):
        try:
            share_types = manila.share_type_list(self.request)
        except Exception:
            exceptions.handle(
                self.request, _('Unable to retrieve share types.'))
            return []
        # Convert dict with extra specs to friendly view
        for st in share_types:
            st.extra_specs = common_utils.metadata_to_str(
                st.extra_specs, 8, 45)
        return share_types


class CreateShareTypeView(forms.ModalFormView):
    form_class = project_forms.CreateShareType
    form_id = "create_share_type"
    template_name = 'admin/share_types/create.html'
    modal_header = _("Create Share Type")
    modal_id = "create_share_type_modal"
    submit_label = _("Create")
    submit_url = reverse_lazy("horizon:admin:share_types:create_type")
    success_url = reverse_lazy('horizon:admin:share_types:index')
    page_title = _("Create Share Type")


class ManageShareTypeAccessView(workflows.WorkflowView):
    workflow_class = st_workflows.ManageShareTypeAccessWorkflow
    template_name = "admin/share_types/manage_access.html"
    success_url = 'horizon:project:share_types:index'
    page_title = _("Manage Share Type Access")

    def get_initial(self):
        return {'id': self.kwargs["share_type_id"]}

    def get_context_data(self, **kwargs):
        context = super(ManageShareTypeAccessView, self).get_context_data(
            **kwargs)
        context['id'] = self.kwargs['share_type_id']
        return context


class UpdateShareTypeView(forms.ModalFormView):
    form_class = project_forms.UpdateShareType
    form_id = "update_share_type"
    template_name = "admin/share_types/update.html"
    modal_header = _("Update Share Type")
    modal_id = "update_share_type_modal"
    submit_label = _("Update")
    submit_url = "horizon:admin:share_types:update_type"
    success_url = reverse_lazy("horizon:admin:share_types:index")
    page_title = _("Update Share Type")

    def get_object(self):
        if not hasattr(self, "_object"):
            st_id = self.kwargs["share_type_id"]
            try:
                self._object = manila.share_type_get(self.request, st_id)
            except Exception:
                msg = _("Unable to retrieve share_type.")
                url = reverse("horizon:admin:share_types:index")
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateShareTypeView, self).get_context_data(**kwargs)
        args = (self.get_object().id,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        share_type = self.get_object()
        return {
            "id": self.kwargs["share_type_id"],
            "name": share_type.name,
            "extra_specs": share_type.extra_specs,
        }
