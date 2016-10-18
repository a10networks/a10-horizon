# Copyright (C) 2014-2016, A10 Networks Inc. All rights reserved.
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

import uuid

POOL_DEFAULTS = {
    "connection_limit": -1,
    "admin_state_up": True
}

MEMBER_DEFAULTS = {
    "weight": 1,
    "admin_state_up": True
}

MONITOR_DEFAULTS = {}


def get_lb_body_from_context(context):
    return {"loadbalancer": {
        "name": context.get("lb_name"),
        "description": context.get("lb_description"),
        "vip_subnet_id": context.get("vip_subnet"),
        "admin_state_up": context.get("admin_state_up")
    }}


def get_listener_body_from_context(context, lb_id=None):
    return {"listener": {
            "name": get_listener_name_from_context(context),
            "description": str(context.get("listener_desc")),
            "loadbalancer_id": str(context.get("loadbalancer_id", lb_id)),
            "protocol": str(context.get("protocol")),
            "protocol_port": context.get("protocol_port")
            }}


def get_ssl_status_from_context(context):
    return context.get("use_ssl", False)


def get_pool_body_from_context(context, listener_id=None):
    or_default = lambda k: context.get(k, POOL_DEFAULTS.get(k))
    name = get_pool_name_from_context(context)
    rv = {"pool": {
        "name": name,
        "description": context.get("description"),
        "listener_id": listener_id or context.get("listener_id"),
        "lb_algorithm": context.get("lb_algorithm"),
        "protocol": context.get("pool_protocol"),
        "admin_state_up": or_default("admin_state_up"),
    }}

    populate_session_persistence_from_context(context, rv)

    return rv


def get_member_body(context, pool_id):
    or_default = lambda k: context.get(k, MEMBER_DEFAULTS.get(k))

    return {"member": {
        "name": context.get("name"),
        "weight": context.get("weight"),
        "address": context.get("member_address"),
        "protocol_port": context.get("member_protocol_port"),
        "subnet_id": context.get("member_subnet_id"),
        "admin_state_up": or_default("admin_state_up"),
        # "pool_id": context.get("pool_id")
    }}


def get_monitor_body(context, pool_id=None):
    or_default = lambda k: context.get(k, MONITOR_DEFAULTS.get(k))
    body = {"healthmonitor": {
        "pool_id": pool_id or context.get("pool_id"),
        "type": str(context.get("monitor_type", "")).upper(),
        "delay": context.get("delay"),
        "timeout": context.get("timeout"),
        "max_retries": context.get("max_retries"),
        "admin_state_up": or_default("admin_state_up")
    }}

    if "HTTP" in body["healthmonitor"].get("type", "").upper():
        body["healthmonitor"]["http_method"] = context.get("http_method")
        body["healthmonitor"]["url_path"] = context.get("url_path")
        body["healthmonitor"]["expected_codes"] = context.get("expected_codes", [200, 201, 202])

    return body


def populate_session_persistence_from_context(context, pool):
    sp = context.get("session_persistence")
    sp_body = {}

    if str(sp).upper() != "NONE":
        sp_body["type"] = str(sp).upper()

    pool["pool"]["session_persistence"] = sp_body

    return pool


def get_listener_name_from_context(context):
    return context.get("listener_name",
                       str("{0}_{1}".format(context.get("protocol"),
                                            context.get("protocol_port"))))


def get_pool_name_from_context(context):
    # TODO(mdurrant) - Pools will need to "key" to their parents.
    return context.get("pool_name") or str(uuid.uuid4())


def get_cert_body_from_context(context):
    rv = {}
    key_map = {
        "name": "cert_name",
        "cert_data": "cert_data",
        "key_data": "key_data",
        "intermediate_data": "intermediate_data",
        "password": "password",
        "description": "description"
    }

    rv = {k: context.get(v) for k, v in key_map.iteritems() if v in context}
    if "certificate_id" in context and "_create" not in context.get("certificate_id", "_create"):
        key_map["certificate_id"] = "id"
        cert_id = context["certificate_id"]
        # get cert details from DB
        rv["id"] = cert_id

    return {"a10_certificate": rv}
