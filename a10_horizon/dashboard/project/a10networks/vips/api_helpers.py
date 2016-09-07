#    Copyright 2014-2016 A10 Networks, Inc.
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
This file provides helper methods for interacting with apis.

These methods use existing display transform / link functions to return
formatted output for special display cases.
"""

from horizon.utils import memoized

# lbaasv2 api
try:
    from neutron_lbaas_dashboard.api import lbaasv2 as lbaasv2_api
except ImportError as ex:
    LOG.exception(ex)
    LOG.warning("Could not import lbaasv2 dashboard API")

from openstack_dashboard.api import neutron as neutron_api

DEFAULT_FILTER = lambda x: True


@memoized.memoized_method
def loadbalancer_field_data(request, **kwargs):
    return [(x.get("id"),
            "{0} - {1}".format(x.get("name"), x.get("vip_address")))
            for x in lbaasv2_api.list_loadbalancers(request, **kwargs)]


@memoized.memoized_method
def listener_field_data(request, pfilter=None, **kwargs):
    default_filter = lambda x: x.get("default_pool_id") is None
    pfilter = pfilter or default_filter

    return [(x.get("id"),
            "{0}".format(x.get("name")))
            for x in lbaasv2_api.list_listeners(request, **kwargs)
            if pfilter(x)]


@memoized.memoized_method
def listener_protocol_field_data(request, **kwargs):
    return [("","Select a protocol"),
                ("TCP", "TCP"),
                ("HTTP", "HTTP"),
                ("HTTPS", "HTTPS"),
                ("TERMINATED_HTTPS", "Terminated HTTPS")
        ]


@memoized.memoized_method
def pool_field_data(request, pfilter=DEFAULT_FILTER, **kwargs):
    return [(x.get("id"),
            "{1} - {0}".format(x.get("name"), x.get("protocol")))
            for x in lbaasv2_api.pool_list(request, **kwargs) if pfilter(x)]


@memoized.memoized_method
def lb_algorithm_field_data(request, insert_empty=True):
    rv = [("ROUND_ROBIN", "Round Robin"),
            ("LEAST_CONNECTIONS", "Least Connections"),
            ("SOURCE_IP", "Source IP Address")]

    if insert_empty:
        rv.insert(0, ("", "Select an algorithm"))
    return rv


@memoized.memoized_method
def pool_protocol_field_data(request):
    return [("", "Select a protocol"),
            ("HTTP", "HTTP"),
            ("HTTPS", "HTTPS"),
            ("TCP", "TCP")
    ]


@memoized.memoized_method
def session_persistence_field_data(request, lowercase_values=True):
    upper_transform = lambda x: str(x).upper()
    lower_transform = lambda x: str(x).lower()
    value_transform =  lower_transform if lowercase_values else upper_transform

    return [
                ("NONE", "None"),
                (value_transform("source_ip"), "Source IP"),
                (value_transform("http_cookie"), "HTTP Cookie"),
                (value_transform("app_cookie"), "App Cookie")
    ]


@memoized.memoized_method
def healthmonitor_type_field_data(request):
    return [("", "Select a monitor type"),
            ("http", "HTTP"),
            ("https", "HTTPS"),
            ("ping", "PING"),
            ("tcp", "TCP")
    ]


def healthmonitor_httpmethod_field_data(request):
    return [("", "Select an HTTP Method"),
            ("GET", "GET"),
            ("POST", "POST")
    ]


@memoized.memoized_method
def subnet_field_data(request):
    transform_func = lambda x: (x.get("id"), "{0} - {1}".format(x.get("name"), x.get("cidr")))
    return sorted([transform_func(x) for x in neutron_api.subnet_list(request)],
                  key=lambda x: x[0])
