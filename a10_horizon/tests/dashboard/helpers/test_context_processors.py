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

from a10_horizon.dashboard.helpers import context_processors as target

VIP = "vip"
MEMBER = "member"
POOL = "pool"
MONITOR = "monitor"
PORT = "port"
LISTENER = "listener"
LB = "loadbalancer"
SUBNET = "subnet"


DEFAULT_IDS = {
    SUBNET: "subnet01",
    VIP: "vip01",
    MEMBER: "member01",
    POOL: "pool01",
    LISTENER: "listener01",
    LB: "loadbalancer01"
}


def default_id(type, default=None):
    return DEFAULT_IDS.get(type, default or "id01")


class AttributeDict(dict):

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class TestBase(unittest2.TestCase):

    def setUp(self):
        self._init_mocks()

    def tearDown(self):
        pass

    def _init_mocks(self):
        self.context = None
        uuid.uuid4 = mock.MagicMock(return_value="abc")

    def _get_member(self):
        return {
            "weight": 5,
            "admin_state_up": False,
            "member_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
            "member_address": "10.0.0.8",
            "member_protocol_port": 80
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
            rv.update({
                "http_method": "GET",
                "url_path": "/index.html",
                "expected_codes": "200,201,202"
            })
        return {"healthmonitor": rv}

    def _get_subnet(self):
        return {"subnet": {
                "id": default_id(SUBNET),
                "name": "vipnet",
                "cidr": "192.168.1.0/24",
                "ip_version": 4  # has to be an int
                }}

    def _get_pool(self, is_request=False, **kwargs):
        rv = {"pool": {
            "name": "pool01",
            "description": "pool01",
            "listener_id": default_id(LISTENER),
            "protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "admin_state_up": True,
            "session_persistence": {
            }
        }}

        if is_request:
            rv.update(kwargs)

        return rv

    def _get_pool_obj(self, *args, **kwargs):
        return FakePool(*args, **kwargs)

    def _get_port(self):
        return {"port": {}}

    def _get_lb(self):
        return {"loadbalancer": {
            "name": "testlb",
            "description": "test lb",
            "admin_state_up": True,
            "vip_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
        }}

    def _build_listener(self, **kwargs):
        return {"listener": {
            "name": "HTTP_666",
            "description": "Listener Description",
            "loadbalancer_id": default_id(LB),
            "protocol": "HTTP",
            "protocol_port": 666,
            # "connection_limit": -1,
            # "admin_state_up": True,
        }}

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
                        "id": default_id(LISTENER),
                        "operating_status": "ONLINE",
                        "provisioning_status": "ACTIVE",
                        "pools": [
                            {
                                "id": default_id(POOL),
                                "operating_status": "ONLINE",
                                "provisioning_status": "ACTIVE",
                                "members": [
                                    {
                                        "id": default_id(MEMBER),
                                        "operating_status": "ONLINE",
                                        "provisioning_status": "ACTIVE"
                                    }
                                ],
                                "healthmonitor": {
                                    "id": default_id(MEMBER),
                                    "provisioning_status": "ACTIVE"
                                }
                            }
                        ]
                    }
                ]
            }
        }

    def _get_certificate(self):
        return {
            "a10_certificate": {
                "name": "FAKE",
                "cert_data": "FAKE_CERT",
                "intermediate_data": "FAKE CA",
                "key_data": "FAKE KEY",
                "description": "FAKE",
                "password": "S00perS3cret"
            }

        }

    def _build_lb_context(self):
        return {
            "lb_name": "testlb",
            "lb_description": "test lb",
            "admin_state_up": True,
            "vip_subnet": "013d3059-87a4-45a5-91e9-d721068ae0b2",
        }

    def _build_listener_context(self):
        return {
            "name": "HTTP_666",
            "protocol": "HTTP",
            "protocol_port": 666,
            "loadbalancer_id": DEFAULT_IDS.get(LB),
            "listener_desc": "Listener Description",
        }

    def _build_pool_context(self, sp_type=None, cookie_name=None):
        return {
            "name": "pool01",
            "description": "the description",
            "listener_id": default_id(LISTENER),
            "pool_protocol": "HTTP",
            "lb_algorithm": "ROUND_ROBIN",
            "admin_state_up": True,
            "session_persistence": sp_type,
            "cookie_name": cookie_name
        }

    def _build_member_context(self):
        return {"weight": 5,
                "admin_state_up": False,
                "member_subnet_id": "013d3059-87a4-45a5-91e9-d721068ae0b2",
                "member_address": "10.0.0.8",
                "member_protocol_port": 80}

    def _build_monitor_context(self, monitor_type="PING"):
        rv = {
            "pool_id": "74aa2010-a59f-4d35-a436-60a6da882819",
            "monitor_type": monitor_type,
            "delay": "1",
            "timeout": 1,
            "max_retries": 5,
            "admin_state_up": True
        }

        if "http" in str(monitor_type).lower():
            rv.update({
                "http_method": "GET",
                "url_path": "/index.html",
                "expected_codes": "200,201,202"
            })
        return rv

    def _build_certificate_context(self, **kwargs):
        return {
            "cert_name": kwargs.get("name"),
            "cert_data": kwargs.get("cert_data"),
            "key_data": kwargs.get("key_data"),
            "intermediate_data": kwargs.get("intermediate_data"),
            "password": kwargs.get("password"),
            "description": kwargs.get("description")
        }


class TestContextProcessors(TestBase):

    # Load Balancers
    def test_get_lb_body_from_context(self):
        expected = self._get_lb()
        context = self._build_lb_context()
        actual = target.get_lb_body_from_context(context)
        self.assertEqual(expected, actual)

    def test_get_listener_body_from_context(self):
        expected = self._get_listener()
        context = self._build_listener_context()
        actual = target.get_listener_body_from_context(context, default_id(LB))
        self.assertEqual(expected, actual)

    def test_get_listener_body_from_context_sets_loadbalancer_id(self):
        expected = self._get_listener()
        lb_id = default_id(LB)
        context = self._build_listener_context()
        actual = target.get_listener_body_from_context(context, lb_id)
        self.assertEqual(expected, actual)

    def test_get_pool_body_from_context(self):
        expected = self._get_pool()
        context = self._build_pool_context()
        actual = target.get_pool_body_from_context(context)
        self.assertEqual(expected, actual)

    def test_get_pool_body_from_context_name(self):
        expected = self._get_pool()
        context = self._build_pool_context()
        actual = target.get_pool_body_from_context(context)

    def _test_get_pool_body_from_context_session_persistence(self, sp_type=None, cookie_name=None):
        context = self._build_pool_context(sp_type, cookie_name)
        expected = self._get_pool()
        target.populate_session_persistence_from_context(context, expected)
        actual = target.get_pool_body_from_context(context)
        self.assertEqual(expected, actual)

    def test_get_pool_body_from_context_session_persistence_none(self):
        self._test_get_pool_body_from_context_session_persistence(None)

    def test_get_pool_body_from_context_session_persistence_app_cookie(self):
        self._test_get_pool_body_from_context_session_persistence("APP_COOKIE", "mahcookie")

    def test_get_pool_body_from_context_session_persistence_source_ip(self):
        self._test_get_pool_body_from_context_session_persistence("SOURCE_IP")

    def test_get_pool_body_from_context_session_persistence_source_ip(self):
        self._test_get_pool_body_from_context_session_persistence("HTTP_COOKIE")

    def test_get_pool_body_from_context(self):
        expected = self._get_pool()
        context = self._build_pool_context()
        actual = target.get_pool_body_from_context(context)
        self.assertEqual(expected, actual)

    def test_get_member_body(self):
        expected = self._get_member()
        context = self._build_member_context()
        actual = target.get_member_body(context, default_id(POOL))

    def _test_get_monitor_body(self, **kwargs):
        expected = self._get_monitor(**kwargs)
        context = self._build_monitor_context(**kwargs)
        actual = target.get_monitor_body(context)
        self.assertEqual(expected, actual)

    def test_get_monitor_body_monitor_type_HTTP(self):
        self._test_get_monitor_body(monitor_type="HTTP")

    def test_get_monitor_body_monitor_type_HTTPS(self):
        self._test_get_monitor_body(monitor_type="HTTPS")

    def test_get_monitor_body_monitor_type_PING(self):
        self._test_get_monitor_body(monitor_type="PING")

    def test_get_listener_name_from_context(self):
        context = {
            "protocol": "HTTP",
            "protocol_port": 666
        }

        expected = "{0}_{1}".format(context.get("protocol"), context.get("protocol_port"))
        actual = target.get_listener_name_from_context(context)
        self.assertEqual(expected, actual)

    def _test_get_pool_name_from_context(self, expected, name=None):
        context = {"name": name}
        actual = target.get_pool_name_from_context(context)
        self.assertEqual(expected, actual)

    def test_get_pool_name_from_context_if_name_specified(self):
        self._test_get_pool_name_from_context("expected", "expected")

    def test_get_pool_name_from_context_if_name_unspecified(self):
        self._test_get_pool_name_from_context(uuid.uuid4())

    def test_get_cert_body_from_context(self):
        expected = self._get_certificate()
        context = self._build_certificate_context(**expected.get("a10_certificate"))
        actual = target.get_cert_body_from_context(context)
        self.assertEqual(expected, actual)
