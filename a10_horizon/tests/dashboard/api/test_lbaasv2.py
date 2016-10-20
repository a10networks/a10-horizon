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

# from django.conf import settings
# from django import http
# from django.test.utils import override_settings
import mock
import sys
import unittest2

# import these before the whole module gets imported.
# this lets us use classes for the tests
# while mocking dependencies.
# from a10_horizon.dashboard.api.lbaasv2 import LoadBalancer
# from a10_horizon.dashboard.api.lbaasv2 import Listener
# from a10_horizon.dashboard.api.lbaasv2 import Member
# from a10_horizon.dashboard.api.lbaasv2 import Pool
# from a10_horizon.dashboard.api.lbaasv2 import HealthMonitor


SUBNET_ID = "subnet01"
VIP_ID = "vip01"
MEMBER_ID = "member01"
POOL_ID = "pool01"
MONITOR_ID = "monitor01"
PORT_ID = "port01"
LISTENER_ID = "listener01"
LB_ID = "loadbalancer01"


def mock_return(arg):
    return arg


class AttributeDict(dict):

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class TestBase(unittest2.TestCase):

    def _get_request(self):
        return mock.MagicMock(user=mock.MagicMock(
            service_catalog=self._get_service_catalog(),
            services_region="RegionOne",
            token=mock.MagicMock(id="tokenid")))

    def _get_service_catalog(self):
        return [
            {
                "url": "http://localhost/identity",
                "type": "identity",
                "endpoints": [
                    {
                        "interface": "public",
                        "region": "RegionOne",
                        "url": "http://localhost/identity"
                    }
                ],
            },
            {
                "url": "http://localhost:9696",
                "type": "network",
                "endpoints": [
                    {
                        "interface": "public",
                        "region": "RegionOne",
                        "url": "http://localhost:9696"
                    }
                ]
            }
        ]

    def _get_member(self):
        return {
            "weight": 5,
            "admin_state_up": False,
            "subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
            "tenant_id": "1a3e005cf9ce40308c900bcb08e5320c",
            "address": "10.0.0.8",
            "protocol_port": 80,
            "id": "9a7aff27-fd41-4ec1-ba4c-3eb92c629313"
        }

    def _get_monitor(self, monitor_type="PING"):
        rv = {
            "pool_id": "74aa2010-a59f-4d35-a436-60a6da882819",
            "type": monitor_type,
            "delay": "1",
            "timeout": 1,
            "max_retries": 5,
            "admin_state_up": True
        }

        if "http" in str(monitor_type).lower():
            rv.udpate({
                "http_method": "GET",
                "url_path": "/index.html",
                "expected_codes": "200,201,202"
            })
        return rv

    def _get_subnet(self):
        return {"subnet": {
            "id": SUBNET_ID,
                "name": "vipnet",
                "cidr": "192.168.1.0/24",
                "ip_version": 4  # has to be an int
                }}

    def _get_pool(self, is_request=False, **kwargs):
        rv = {
            # "id": POOL_ID,
            "name": "pool01",
            "description": "Test Pool",
            "listener_id": LISTENER_ID,
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "admin_state_up": True,
            "session_persistence": {
                "type": None
            }
        }

        if is_request:
            rv.update(kwargs)

        return rv

    def _get_pool_obj(self, *args, **kwargs):
        return FakePool(*args, **kwargs)

    def _get_port(self):
        return {"port": {}}

    def _get_lb(self):
        return {
            'id': VIP_ID,
            'name': "testlb",
            'description': "Test LB",
            'admin_state_up': "ONLINE",
            'provisioning_state': "ONLINE",
            "listeners": [{}],
            "vip_address": "10.0.0.4",
            "vip_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
        }

    def _build_listener(self, **kwargs):
        return {
            # "id": kwargs.get("id", LISTENER_ID),
            "name": kwargs.get("name", LISTENER_ID),
            "description": kwargs.get("description", LISTENER_ID),
            "loadbalancer_id": kwargs.get("loadbalancer_id", LB_ID),
            "protocol": kwargs.get("protocol"),
            "protocol_port": kwargs.get("protocol_port"),
            "connection_limit": kwargs.get("connection_limit"),
            "admin_state_up": kwargs.get("admin_state_up", True),
        }

    def _get_listener(self):
        return self._build_listener()

    def _get_lbgraph(self):
        return {"loadbalancer": {
            "listener": {},
            "pool": {},
            "members": [{}],
        }}

    def _get_lbstats(self):
        return {
            "loadbalancer": {
                "bytes_in": 0,
                "bytes_out": 0,
                "connections": 0,
                "active_connections": 0
            }
        }

    def _get_lbstatus(self):
        return {
            "loadbalancer": {
                "operating_status": "ONLINE",
                "provisioning_status": "ACTIVE",
                "listeners": [
                    {
                        "id": LISTENER_ID,
                        "operating_status": "ONLINE",
                        "provisioning_status": "ACTIVE",
                        "pools": [
                            {
                                "id": POOL_ID,
                                "operating_status": "ONLINE",
                                "provisioning_status": "ACTIVE",
                                "members": [
                                    {
                                        "id": MEMBER_ID,
                                        "operating_status": "ONLINE",
                                        "provisioning_status": "ACTIVE"
                                    }
                                ],
                                "healthmonitor": {
                                    "id": MONITOR_ID,
                                    "provisioning_status": "ACTIVE"
                                }
                            }
                        ]
                    }
                ]
            }
        }


class TestLbaasV2API(TestBase):

    def list_healthmonitors_hack(self, *args, **kwargs):
        # This terrible function replicates the behavior of the lbaasv2 api in regard to HM listing
        # If kwargs is None, it returns a list.
        # If kwargs >= {}, it returns a generator.
        rv = [self._get_monitor()]
        ret_transform = lambda x: {"healthmonitors": x}
        if kwargs is not None:
            ret_transform = lambda x: iter([{"healthmonitors": x}])

        return ret_transform(rv)

    def setUp(self):
        self._init_mocks()
        from a10_horizon.dashboard.api import lbaasv2
        # from openstack_dashboard import api
        lbaasv2.neutronclient = self.neutronclient_mock
        self.request = self._get_request()

        self.target = lbaasv2

    def tearDown(self):
        self.mock_patcher.stop()

    def _init_mocks(self):
        self.subnet = self._get_subnet()

        self.neutronclient_mock = mock.MagicMock()

        mock_modules = {
            "glanceclient.v2.client": mock.MagicMock(),
            # "horizon": mock.MagicMock(),
            # "openstack_dashboard.api.base": mock.MagicMock(),
            "horizon.utils.escape": mock.MagicMock(),
            "openstack_dashboard.api.glance.glanceclient": mock.MagicMock(),
            "neutronclient.v2_0": mock.MagicMock(),
            "openstack_dashboard.api.neutron.neutronclient": mock.MagicMock(
                return_value=self.neutronclient_mock),
            "django.utils.html.escape": mock.MagicMock(),
            "django.utils.functional.__mod__": lambda lhs, **rhs: lhs.format(rhs),
            "django.utils.translation.ugettext_lazy": mock.MagicMock(return_value=lambda **x: x)
        }

        # Mocking all of openstack_dashboard.api.neutron causes big problems
        # These are patched because the lbaasv2 API makes calls to both neutronclient (lbaas)
        # and horizon's neutron API (base neutron).

        self.mock_patcher = mock.patch.dict("sys.modules", mock_modules)
        self.mock_patcher.start()

        # I don't like this mock setup. It's WAY too specific.
        # Unfortunately, since neutronclient is dynamic in that extensions will define
        # what methods may or may not exist on the resulting object
        # We have to specify the methods we know we want.
        self.neutronclient_mock.return_value = mock.Mock(
            # Load Balancer
            create_loadbalancer=mock.Mock(return_value={"loadbalancer": self._get_lb()}),
            show_loadbalancer=mock.Mock(return_value={"loadbalancer": self._get_lb()}),
            list_loadbalancers=mock.Mock(return_value={"loadbalancers": [self._get_lb()]}),
            delete_loadbalancer=mock.Mock(side_effect=lambda x: True),
            update_loadbalancer=mock.Mock(side_effect=lambda lb_id, x: {"loadbalancer": x}),
            retrieve_loadbalancer_status=mock.Mock(
                side_effect=lambda id: {"statuses": self._get_lbstatus()}),
            retrieve_loadbalancer_stats=mock.Mock(
                side_effect=lambda id: {"stats": self._get_lbstats()}),
            # Listener
            create_listener=mock.Mock(return_value={"listener": self._get_listener()}),
            list_listeners=mock.Mock(return_value={"listeners": [self._get_listener()]}),
            show_listener=mock.Mock(return_value={"listener": self._get_listener()}),
            update_listener=mock.Mock(side_effect=lambda id, x: {"listener": x}),
            # Pool
            create_lbaas_pool=mock.MagicMock(return_value={"pool": self._get_pool()}),
            show_lbaas_pool=mock.MagicMock(return_value={"pool": self._get_pool()}),
            list_lbaas_pools=mock.MagicMock(return_value={"pools": [self._get_pool()]}),
            update_lbaas_pool=mock.MagicMock(side_effect=lambda id, x: {"pool": x}),
            delete_lbaas_pool=mock.MagicMock(side_effect=lambda x: True),
            # Member
            create_lbaas_member=mock.MagicMock(return_value={"member": self._get_member()}),
            show_lbaas_member=mock.MagicMock(return_value={"member": self._get_member()}),
            list_lbaas_members=mock.MagicMock(return_value={"members": [self._get_member()]}),
            update_lbaas_member=mock.MagicMock(side_effect=lambda pool_id, id, x: {"member": x}),
            delete_lbaas_member=mock.MagicMock(side_effect=lambda pool_id, id: True),
            # Health Monitor
            create_lbaas_healthmonitor=mock.MagicMock(
                return_value={"healthmonitor": self._get_monitor()}),
            show_lbaas_healthmonitor=mock.MagicMock(
                return_value={"healthmonitor": self._get_monitor()}),
            # This call has an interesting implementation just past the API
            # If you call list_lbaas_healthmonitors with an empty dictionary, it returns a generator.
            # If you call * with None, it returns a list.
            list_lbaas_healthmonitors=mock.MagicMock(
                side_effect=self.list_healthmonitors_hack),
            update_lbaas_healthmonitor=mock.MagicMock(
                side_effect=lambda id, x: {"healthmonitor": x}),
            delete_lbaas_healthmonitor=mock.MagicMock(side_effect=lambda id: True),
            # subnet_get=mock.MagicMock(return_value={"subnet": self._get_subnet()}),
            # list_subnets=mock.MagicMock(
            #     return_value={"subnets": [self._get_subnet().get("subnet")]}),
            # list_members=mock.MagicMock(return_value={"members": [self._get_member()]}),
            # list_health_monitors=mock.MagicMock(
            #     return_value={"health_monitors": [self._get_monitor()]}),
            # show_port=mock.MagicMock(return_value=self._get_port())
        )

    # Load Balancers
    def test_list_loadbalancers(self):
        expected = [self._get_lb()]
        list_args = {}
        actual = self.target.list_loadbalancers(self.request, **list_args)
        list_call = self.neutronclient_mock.return_value.list_loadbalancers
        list_call.assert_called_with(**list_args)
        self.assertEqual(expected, actual)

    def _test_get_loadbalancer(self):
        expected = self._get_lb()
        actual = self.target.get_loadbalancer(self.request, expected.get("id"))
        get_call = self.neutronclient_mock.return_value.show_loadbalancer
        get_call.assert_called_with(expected.get("id"))
        return expected, actual

    def test_create_loadbalancer(self):
        expected = self._get_lb()
        actual = self.target.create_loadbalancer(self.request, expected)
        create_call = self.neutronclient_mock.return_value.create_loadbalancer
        self.assertTrue(create_call.called)
        create_call.assert_called_with(expected)
        self.assertEqual(expected, actual)

    def test_get_loadbalancer(self):
        expected, actual = self._test_get_loadbalancer()

    def test_update_loadbalancer(self):
        expected = self._get_lb()
        actual = self.target.update_loadbalancer(self.request, expected.get("id"), **expected)
        update_call = self.neutronclient_mock.return_value.update_loadbalancer
        self.assertTrue(update_call.called)
        update_call.assert_called_with(expected.get("id"), expected)

    def test_delete_loadbalancer(self):
        lb = self._get_lb()
        self.target.delete_loadbalancer(self.request, lb.get("id"))
        delete_call = self.neutronclient_mock.return_value.delete_loadbalancer
        self.assertTrue(delete_call.called)

    def test_loadbalancer_status(self):
        expected = self._get_lbstatus()
        actual = self.target.get_loadbalancer_status(self.request, LB_ID)
        status_call = self.neutronclient_mock.return_value.retrieve_loadbalancer_status
        self.assertTrue(status_call.called)
        status_call.assert_called_with(LB_ID)

    def test_loadbalancer_stats(self):
        expected = self._get_lbstats()
        actual = self.target.get_loadbalancer_stats(self.request, LB_ID)
        stats_call = self.neutronclient_mock.return_value.retrieve_loadbalancer_stats
        self.assertTrue(stats_call.called)
        stats_call.assert_called_with(LB_ID)

    # Listeners
    def test_create_listener(self):
        expected = self._get_listener()
        actual = self.target.create_listener(self.request, expected)
        create_call = self.neutronclient_mock.return_value.create_listener
        self.assertTrue(create_call.called)
        create_call.assert_called_with(expected)
        self.assertEqual(expected, actual)

    def test_show_listener(self):
        expected = self._get_listener()
        actual = self.target.show_listener(self.request, expected.get("id"))
        show_call = self.neutronclient_mock.return_value.show_listener
        self.assertTrue(show_call.called)
        show_call.assert_called_with(expected.get("id"))
        self.assertEqual(expected, actual)

    def test_list_listeners(self):
        expected = [self._get_listener()]
        list_args = {}
        actual = self.target.list_listeners(self.request, **list_args)
        list_call = self.neutronclient_mock.return_value.list_listeners
        list_call.assert_called_with(**list_args)
        self.assertEqual(expected, actual)

    def test_update_listener(self):
        expected = self._get_listener()
        # gotta change something or it's not an update.
        expected["name"] = "newlistenername"
        actual = self.target.update_listener(self.request, expected.get("id"), **expected)
        update_call = self.neutronclient_mock.return_value.update_listener
        self.assertTrue(update_call.called)
        update_call.assert_called_with(expected.get("id"), expected)
        self.assertEqual(expected, actual)

    def test_delete_listener(self):
        expected = self._get_listener().get("id")
        self.target.delete_listener(self.request, expected)
        delete_call = self.neutronclient_mock.return_value.delete_listener
        self.assertTrue(delete_call.called)
        delete_call.assert_called_with(expected)

    # Pools
    def test_create_pool(self):
        expected = self._get_pool()
        actual = self.target.pool_create(self.request, **expected)
        create_call = self.neutronclient_mock.return_value.create_lbaas_pool
        self.assertTrue(create_call.called)
        create_call.assert_called_with({"pool": expected})

    def test_get_pool(self):
        expected = self._get_pool()
        pool_id = "pool01"
        actual = self.target.pool_get(self.request, pool_id)
        get_call = self.neutronclient_mock.return_value.show_lbaas_pool
        self.assertTrue(get_call.called)
        get_call.assert_called_with(pool_id)
        self.assertEqual(expected, actual)

    def test_list_pools(self):
        expected = [self._get_pool()]
        list_args = {}
        actual = self.target.pool_list(self.request, **list_args)
        list_call = self.neutronclient_mock.return_value.list_lbaas_pools
        list_call.assert_called_with(**list_args)
        # override obj comparison with dict comparison
        self.assertEqual(expected, actual)

    def test_update_pool(self):
        pool_id = POOL_ID
        expected = self._get_pool()
        expected["name"] = "newpool"
        actual = self.target.pool_update(self.request, pool_id, **expected)

        update_call = self.neutronclient_mock.return_value.update_lbaas_pool
        self.assertTrue(update_call.called)
        update_call.assert_called_with(pool_id, expected)
        self.assertTrue(expected, expected)

    def test_delete_pool(self):
        pool_id = POOL_ID
        self.target.pool_delete(self.request, pool_id)
        delete_call = self.neutronclient_mock.return_value.delete_lbaas_pool
        self.assertTrue(delete_call.called)
        delete_call.assert_called_with(pool_id)

    def test_create_member(self):
        expected = self._get_member()
        actual = self.target.member_create(self.request, POOL_ID, expected)
        create_call = self.neutronclient_mock.return_value.create_lbaas_member
        self.assertTrue(create_call.called)
        create_call.assert_called_with(POOL_ID, expected)

    def test_get_member(self):
        expected = self._get_member()
        actual = self.target.member_get(self.request, POOL_ID, MEMBER_ID)
        get_call = self.neutronclient_mock.return_value.show_lbaas_member
        self.assertTrue(get_call.called)
        get_call.assert_called_with(MEMBER_ID, POOL_ID)

    def test_list_members(self):
        expected = [self._get_member()]
        list_args = {}
        actual = self.target.member_list(self.request, POOL_ID, **list_args)
        list_call = self.neutronclient_mock.return_value.list_lbaas_members
        self.assertTrue(list_call.called)
        list_call.assert_called_with(POOL_ID, **list_args)

    def test_update_member(self):
        expected = self._get_member()
        expected["weight"] = 42
        actual = self.target.member_update(self.request, POOL_ID, MEMBER_ID, **expected)
        update_call = self.neutronclient_mock.return_value.update_lbaas_member
        self.assertTrue(update_call.called)
        update_call.assert_called_with(MEMBER_ID, POOL_ID, expected)

    def test_delete_member(self):
        self.target.member_delete(self.request, MEMBER_ID, POOL_ID)
        delete_call = self.neutronclient_mock.return_value.delete_lbaas_member
        self.assertTrue(delete_call.called)
        delete_call.assert_called_with(MEMBER_ID, POOL_ID)

    def _test_create_healthmonitor(self, monitor_type="PING"):
        # HTTP monitors have an if block that sets the HTTP params
        # None of these items should be present in non-HTTP monitors
        expected = self._get_monitor()
        expected["type"] = monitor_type
        self.target.healthmonitor_create(self.request, **expected)
        create_call = self.neutronclient_mock.return_value.create_lbaas_healthmonitor
        self.assertTrue(create_call.called)
        create_call.assert_called_with({"healthmonitor": expected})

    def test_create_healthmonitor_nonhttp(self):
        self._test_create_healthmonitor("PING")

    def test_create_healthmonitor_http(self):
        self._test_create_healthmonitor("HTTP")

    def test_create_healthmonitor_nonhttps(self):
        self._test_create_healthmonitor("HTTPS")

    def test_get_healthmonitor(self):
        expected = self._get_monitor()
        actual = self.target.healthmonitor_get(self.request, MONITOR_ID)
        get_call = self.neutronclient_mock.return_value.show_lbaas_healthmonitor
        self.assertTrue(get_call.called)
        get_call.assert_called_with(MONITOR_ID)
        self.assertTrue(expected, actual)

    def test_list_healthmonitors(self):
        expected = [self._get_monitor()]
        list_args = {}
        actual = self.target.healthmonitor_list(self.request, **list_args)

        list_call = self.neutronclient_mock.return_value.list_lbaas_healthmonitors
        self.assertTrue(list_call.called)
        list_call.assert_called_with(list_args)
        self.assertTrue(expected, actual)

    def test_update_healthmonitor(self):
        expected = self._get_monitor()
        expected["timeout"] = 42
        actual = self.target.healthmonitor_update(self.request, MONITOR_ID, **expected)

        update_call = self.neutronclient_mock.return_value.update_lbaas_healthmonitor
        self.assertTrue(update_call)
        update_call.assert_called_with(MONITOR_ID, expected)
        self.assertEqual({"healthmonitor": expected}, actual)
