# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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

import mock
import sys
import unittest2

import uuid

from a10_horizon.dashboard.helpers import ui_helpers as target

class TestUiHelpers(unittest2.TestCase):

    def setUp(self):
        self._init_mocks()


    def tearDown(self):
        pass

    def _init_mocks(self):
        self.context = None
        uuid.uuid4 = mock.MagicMock(return_value="abc")

    def def_switchable_field_is_switchable(self):
        expected = "switchable"
        actual = target.switchable_field("test")
        self.assertEqual(expected, actual.get("class"))

    def test_switchable_field_data_slug(self):
        expected = "test"
        actual = target.switchable_field(expected)
        self.assertEqual(expected, actual.get("data-slug"))

    def def_switched_field_is_switched(self):
        expected = "switched"
        actual = target.switched_field("test")
        self.assertEqual(expected, actual.get("class"))

    def test_switchable_field_data_slug(self):
        expected = "test"
        actual = target.switched_field(expected)
        self.assertEqual(expected, actual.get("data-switch-on"))

    def test_switchable_field_data_attrs(self):
        slug = "blah"
        expected = "testswitch"
        title = "title"
        expected_key = "data-{0}-{1}".format(slug, expected)
        actual = target.switched_field(slug, {expected: title})
        self.assertEqual(title, actual.get(expected_key))

    def test_textarea_size_defaults(self):
        expected = {"cols": 25, "rows": 10}
        actual = target.textarea_size()
        self.assertEqual(expected, actual)
