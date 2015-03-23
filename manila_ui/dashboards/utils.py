# All Rights Reserved.
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

from django.forms import ValidationError  # noqa
from django.utils.translation import ugettext_lazy as _


def parse_str_meta(meta_s):
    """Parse multiline string with data from form.

    :option meta_s: str - string with keys and values
    :returns: tuple of dict with key-value for set and list with keys for unset
    :raises: ValidationError
    """
    strings = [el.strip() for el in meta_s.split("\n") if len(el.strip()) > 0]
    set_dict = {}
    unset_list = []
    msg = ""
    for string in strings:
        if string.count("=") == 1:
            pair = [p.strip() for p in string.split("=")]
            if not all(len(p) in range(1, 256) for p in pair):
                msg = _("All keys and values must be in range from 1 to 255.")
            elif pair[0] in set_dict.keys():
                msg = _("Duplicated keys '%s'.") % pair[0]
            elif any(" " in p for p in pair):
                msg = _("Keys and values should not contain spaces. "
                        "Error in '%s'.") % string
            else:
                set_dict[pair[0]] = pair[1]
        elif string.count("=") == 0:
            s = string.strip()
            if len(s) not in range(1, 256):
                msg = _("Key '%s' has inproper length.") % s
            elif " " in s:
                msg = _("Key can not contain spaces. See string '%s'.") % s
            elif s not in unset_list:
                unset_list.append(s)
        else:
            msg = _("Wrong data provided in string '%s'.") % string
    duplicated_keys = [uk for uk in unset_list if uk in set_dict.keys()]
    if duplicated_keys:
        msg = _("Duplicated keys '%s'.") % str(duplicated_keys)
    if msg:
        raise ValidationError(message=msg)
    return set_dict, unset_list


def metadata_to_str(metadata):
    meta_visible_limit = 4
    text_length_limit = 25
    meta = []
    meta_keys = metadata.keys()
    meta_keys.sort()
    meta_keys = meta_keys[:meta_visible_limit]
    for k in meta_keys:
        k_shortenned = k
        if len(k) > text_length_limit:
            k_shortenned = k[:text_length_limit] + '...'
        v = metadata[k]
        if len(v) > text_length_limit:
            v = v[:text_length_limit] + '...'
        meta.append("%s = %s" % (k_shortenned, v))
    meta_str = "<br/>".join(meta)
    if len(metadata.keys()) > meta_visible_limit:
        meta_str += '...'
    return meta_str
