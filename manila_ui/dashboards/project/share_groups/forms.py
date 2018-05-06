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

from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import memoized
import six

from manila_ui.api import manila


class CreateShareGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"), max_length="255", required=True)
    description = forms.CharField(
        label=_("Description"),
        max_length="255",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateShareGroupForm, self).__init__(request, *args, **kwargs)
        self.st_field_name_prefix = "share-type-choices-"
        self.fields["source_type"] = forms.ChoiceField(
            label=_("Source Type"),
            widget=forms.Select(attrs={
                "class": "switchable",
                "data-slug": "source",
            }),
            required=False)

        self.fields["snapshot"] = forms.ChoiceField(
            label=_("Use share group snapshot as a source"),
            widget=forms.SelectWidget(attrs={
                "class": "switched",
                "data-switch-on": "source",
                "data-source-snapshot": _("Share Group Snapshot"),
            }),
            required=True)

        if ("snapshot_id" in request.GET or
                kwargs.get("data", {}).get("snapshot")):
            try:
                snapshot = self.get_share_group_snapshot(
                    request,
                    request.GET.get(
                        "snapshot_id",
                        kwargs.get("data", {}).get("snapshot")))
                self.fields["name"].initial = snapshot.name
                self.fields["snapshot"].choices = (
                    (snapshot.id, snapshot.name or snapshot.id),
                )
                try:
                    # Set the share group type from the original share group
                    orig_sg = manila.share_group_get(
                        request, snapshot.share_group_id)
                    self.fields["sgt"].initial = orig_sg.share_group_type_id
                except Exception:
                    pass
                del self.fields["source_type"]
            except Exception:
                exceptions.handle(
                    request,
                    _("Unable to load the specified share group snapshot."))
        else:
            source_type_choices = []
            try:
                snapshot_list = manila.share_group_snapshot_list(request)
                snapshots = [s for s in snapshot_list
                             if s.status == "available"]
                if snapshots:
                    source_type_choices.append(("snapshot", _("Snapshot")))
                    self.fields["snapshot"].choices = (
                        [("", _("Choose a snapshot"))] +
                        [(s.id, s.name or s.id) for s in snapshots]
                    )
                else:
                    del self.fields["snapshot"]
            except Exception:
                exceptions.handle(
                    request,
                    _("Unable to retrieve share group snapshots."))

            if source_type_choices:
                choices = ([('none', _("No source, empty share group"))] +
                           source_type_choices)
                self.fields["source_type"].choices = choices
            else:
                del self.fields["source_type"]

            self.fields["az"] = forms.ChoiceField(
                label=_("Availability Zone"),
                widget=forms.SelectWidget(attrs={
                    "class": "switched",
                    "data-switch-on": "source",
                    "data-source-none": _("Availability Zone"),
                }),
                required=False)

            availability_zones = manila.availability_zone_list(request)
            self.fields["az"].choices = (
                [("", "")] + [(az.name, az.name) for az in availability_zones])

            share_group_types = manila.share_group_type_list(request)
            self.fields["sgt"] = forms.ChoiceField(
                label=_("Share Group Type"),
                widget=forms.fields.SelectWidget(attrs={
                    "class": "switched switchable",
                    "data-switch-on": "source",
                    "data-source-none": _("Share Group Type"),
                    "data-slug": "sgt",
                }),
                required=True)
            self.fields["sgt"].choices = (
                [("", "")] + [(sgt.id, sgt.name) for sgt in share_group_types])

            # NOTE(vponomaryov): create separate set of available share types
            # for each of share group types.
            share_types = manila.share_type_list(request)
            for sgt in share_group_types:
                st_choices = (
                    [(st.id, st.name)
                     for st in share_types if st.id in sgt.share_types])
                amount_of_choices = len(st_choices)
                st_field_name = self.st_field_name_prefix + sgt.id
                if amount_of_choices < 2:
                    st_field = forms.ChoiceField(
                        label=_("Share Types"),
                        choices=st_choices,
                        widget=forms.fields.SelectWidget(attrs={
                            "class": "switched",
                            "data-switch-on": "sgt",
                            "data-sgt-%s" % sgt.id: _(
                                "Share Types (one available)"),
                        }),
                        required=True)
                else:
                    height = min(30 * amount_of_choices, 155)
                    st_field = forms.MultipleChoiceField(
                        label=_("Share Types"),
                        choices=st_choices,
                        widget=forms.fields.widgets.SelectMultiple(attrs={
                            "style": "max-height: %spx;" % height,
                            "class": "switched",
                            "data-switch-on": "sgt",
                            "data-sgt-%s" % sgt.id: _(
                                "Share Types (multiple available)"),
                        }),
                        required=False)
                    st_field.initial = st_choices[0]
                self.fields[st_field_name] = st_field

            self.fields["share_network"] = forms.ChoiceField(
                label=_("Share Network"),
                widget=forms.fields.SelectWidget(attrs={
                    "class": "switched",
                    "data-switch-on": "source",
                    "data-source-none": _("Share Network"),
                }),
                required=False)
            share_networks = manila.share_network_list(request)
            self.fields["share_network"].choices = (
                [("", "")] +
                [(sn.id, sn.name or sn.id) for sn in share_networks])

    def clean(self):
        cleaned_data = super(CreateShareGroupForm, self).clean()
        form_errors = list(self.errors)

        for error in form_errors:
            sgt_name = error.split(self.st_field_name_prefix)[-1]
            chosen_sgt = cleaned_data.get("sgt")
            if (error.startswith(self.st_field_name_prefix) and
                    sgt_name != chosen_sgt):
                cleaned_data[error] = "Not set"
                self.errors.pop(error, None)

        source_type = cleaned_data.get("source_type")
        if source_type != "snapshot":
            self.errors.pop("snapshot", None)
            share_group_type = cleaned_data.get("sgt")
            if share_group_type:
                cleaned_data["share_types"] = cleaned_data.get(
                    self.st_field_name_prefix + share_group_type)
                if isinstance(cleaned_data["share_types"], six.string_types):
                    cleaned_data["share_types"] = [cleaned_data["share_types"]]
        else:
            self.errors.pop("sgt", None)

        return cleaned_data

    def handle(self, request, data):
        try:
            source_type = data.get('source_type')
            if (data.get("snapshot") and source_type in (None, 'snapshot')):
                snapshot = self.get_share_group_snapshot(
                    request, data["snapshot"])
                snapshot_id = snapshot.id
                source_sg = manila.share_group_get(
                    request, snapshot.share_group_id)
                data['sgt'] = source_sg.share_group_type_id
            else:
                snapshot_id = None

            share_group = manila.share_group_create(
                request,
                name=data['name'],
                description=data['description'],
                share_group_type=data['sgt'],
                share_types=None if snapshot_id else data.get('share_types'),
                share_network=(
                    None if snapshot_id else data.get('share_network')),
                source_share_group_snapshot=snapshot_id,
                availability_zone=None if snapshot_id else data['az'])

            message = _('Creating share group "%s"') % data['name']
            messages.success(request, message)
            return share_group
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        except Exception:
            exceptions.handle(request, ignore=True)
            self.api_error(_("Unable to create share group."))
            return False

    @memoized.memoized
    def get_share_group_snapshot(self, request, sg_snapshot_id):
        return manila.share_group_snapshot_get(request, sg_snapshot_id)


class UpdateShareGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(
        max_length="255", label=_("Share Group Name"))
    description = forms.CharField(
        widget=forms.Textarea, label=_("Description"), required=False)

    def handle(self, request, data):
        sg_id = self.initial['share_group_id']
        try:
            manila.share_group_update(
                request, sg_id, data['name'], data['description'])
            message = _('Updating share group "%s"') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:share_groups:index")
            exceptions.handle(
                request, _('Unable to update share group.'), redirect=redirect)
            return False
