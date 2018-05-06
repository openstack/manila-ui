# Copyright (c) 2015 Mirantis, Inc.
# All rights reserved.

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

import ddt
from django.forms import ValidationError

from manila_ui.dashboards import utils
from manila_ui.tests import helpers as base


@ddt.ddt
class ManilaDashboardsUtilsTests(base.TestCase):

    @ddt.data(
        ("", {}, []),
        ("  ", {}, []),
        ("\n", {}, []),
        ("f", {}, ["f"]),
        ("f=b", {"f": "b"}, []),
        ("foo=bar", {"foo": "bar"}, []),
        ("\nfoo \n", {}, ["foo"]),
        ("'foo'=\"bar\"\n'bar'", {"foo": "bar"}, ["bar"]),
        ("   foo=   bar ", {"foo": "bar"}, []),
        ("foo= \"<is> bar\"\n", {"foo": "<is> bar"}, []),
        ("\n\nset_me_key = 'value with spaces and equality 2=2'\nunset_key  ",
         {"set_me_key": "value with spaces and equality 2=2"},
         ["unset_key"]),
        ("f" * 255, {}, ["f" * 255]),
        ("f" * 255 + "=" + "b" * 255, {"f" * 255: "b" * 255}, []),
    )
    @ddt.unpack
    def test_parse_str_meta_success(
            self, input_data, expect_set_dict, expected_unset_list):
        set_dict, unset_list = utils.parse_str_meta(input_data)

        self.assertEqual(expect_set_dict, set_dict)
        self.assertEqual(expected_unset_list, unset_list)

    @ddt.data(
        "a b",
        "'a b'",
        "\"a b\"",
        "f" * 256,
        "f" * 256 + "=bar",
        "foo=" + "b" * 256,
        "\"a b \"",
        "foo=bar\nfoo",
        "foo=bar\nfoo=quuz",
    )
    def test_parse_str_meta_validation_error(self, input_data):
        self.assertRaises(ValidationError, utils.parse_str_meta, input_data)

    @ddt.data(
        (({"a": "<script>alert('A')/*", "b": "*/</script>"}, ),
         "a = &lt;script&gt;alert(&apos;A&apos;)/*<br/>b = */&lt;/script&gt;"),
        (({"fookey": "foovalue", "barkey": "barvalue"}, ),
         "barkey = barvalue<br/>fookey = foovalue"),
        (({"foo": "barquuz"}, 1, 2), "fo... = ba..."),
        (({"foo": "barquuz", "zfoo": "zbarquuz"}, 1, 3), "foo = bar..."),
        (({"foo": "barquuz", "zfoo": "zbarquuz"}, 2, 3),
         "foo = bar...<br/>zfo... = zba..."),
        (({"foo": "barquuz", "zfoo": "zbarquuz"}, 3, 3),
         "foo = bar...<br/>zfo... = zba..."),
        (({"foo": "barquuz", "zfoo": "zbarquuz"}, 3, 8),
         "foo = barquuz<br/>zfoo = zbarquuz"),
    )
    @ddt.unpack
    def test_metadata_to_str(self, input_args, expected_output):
        result = utils.metadata_to_str(*input_args)

        self.assertEqual(expected_output, result)

    @ddt.data(
        ("ldap", "LDAP"),
        ("active_directory", "Active Directory"),
        ("kerberos", "Kerberos"),
        ("FaKe", "FaKe"),
    )
    @ddt.unpack
    def test_get_nice_security_service_type(self, input_value, expected_value):
        security_service = type("FakeSS", (object, ), {"type": input_value})()

        result = utils.get_nice_security_service_type(security_service)

        self.assertEqual(expected_value, result)
