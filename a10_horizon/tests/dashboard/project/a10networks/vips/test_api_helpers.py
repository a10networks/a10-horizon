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


class TestApiHelpers(unittest2.TestCase):

    def _get_lb(self, name="lb", vip_address="1.1.1.1"):
        return {
            "name": name,
            "vip_address": vip_address
        }

    def setUp(self):
        # api.neutron = mock.MagicMock()
        self._init_mocks()

    def tearDown(self):
        self.mock_patcher.stop()

    def _init_mocks(self):

        self.request = mock.MagicMock()

        self.neutronapi_mock = mock.MagicMock()
        self.lbaasv2_mock = mock.MagicMock()
        self.neutronclient_mock = mock.MagicMock()

        mock_modules = {
            "horizon": mock.MagicMock(),
            "horizon.messages": mock.MagicMock(),
            "horizon.utils": mock.MagicMock(),
            "horizon.utils.memoized": mock.MagicMock(),
            # "neutron_lbaas_dashboard.api.lbaasv2": self.lbaasv2_mock,
            # "openstack_dashboard": mock.MagicMock(),
            # "openstack_dashboard.api.neutron": self.neutronapi_mock,
            # "openstack_dashboard.api.neutron_api": self.neutronapi_mock,
            "glanceclient.v2.client": mock.MagicMock(),
            "openstack_dashboard.api.glance.glanceclient": mock.MagicMock(),
            "neutronclient.v2_0": mock.MagicMock(),
            "openstack_dashboard.api.neutron.neutronclient": mock.MagicMock(
                return_value=self.neutronclient_mock),
            "django.utils.functional.__mod__": lambda lhs, **rhs: lhs.format(rhs),
            "django.utils.functional.__mod__": lambda lhs, **rhs: lhs.format(rhs),
            "django.utils.translation.ugettext_lazy": mock.MagicMock(return_value=lambda **x: x)
        }

        # Mocking all of openstack_dashboard.api.neutron causes big problems
        # These are patched because the lbaasv2 API makes calls to both neutronclient (lbaas)
        # and horizon's neutron API (base neutron).

        self.mock_patcher = mock.patch.dict("sys.modules", mock_modules)
        self.mock_patcher.start()
        from a10_horizon.dashboard.project.a10networks.vips import api_helpers
        self.target = api_helpers

    def test_loadbalancer_field_data_results(self):
        expected = [self._get_lb(), self._get_lb()]
        self.lbaasv2_mock.list_loadbalancers = mock.MagicMock(
            side_effect=lambda: expected)
        actual = self.target.loadbalancer_field_data(self.request, {})
        self.assertEqual(len(expected), len(actual))
