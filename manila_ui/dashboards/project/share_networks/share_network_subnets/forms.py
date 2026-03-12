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

from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from manila_ui.api import manila
from manila_ui.dashboards import utils


class UpdateShareNetworkSubnetMetadataForm(forms.SelfHandlingForm):
    share_network_id = forms.CharField(widget=forms.HiddenInput())
    subnet_id = forms.CharField(widget=forms.HiddenInput())
    metadata = forms.CharField(label=_("Metadata"),
                               widget=forms.Textarea(),
                               required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "metadata" in self.initial:
            meta_str = ""
            for k, v in self.initial["metadata"].items():
                meta_str += f"{k}={v}\r\n"
            self.initial["metadata"] = meta_str

    def handle(self, request, data):
        share_network_id = self.initial['share_network_id']
        subnet_id = self.initial['subnet_id']
        try:
            set_dict, unset_list = utils.parse_str_meta(data['metadata'])
            share_network = manila.share_network_get(request, share_network_id)
            if set_dict:
                manila.share_network_subnet_set_metadata(
                    request, share_network, subnet_id, set_dict)
            if unset_list:
                manila.share_network_subnet_delete_metadata(
                    request, share_network, subnet_id, unset_list)
            messages.success(
                request, _('Share Network Subnet metadata updated.'))
            return True
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        except Exception as e:
            if "MetadataItemNotFound" in str(e) or getattr(
                e, 'code', None) == 404:
                msg = _("Invalid format: Each line must contain a 'key=value' "
                        "pair. If you intended to delete a key, ensure the "
                        "key exists.")
                messages.error(request, msg)
            else:
                exceptions.handle(
                    request, _('Unable to update network subnet metadata.'))
            return False
