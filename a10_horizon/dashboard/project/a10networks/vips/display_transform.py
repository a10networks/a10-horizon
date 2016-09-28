#    Copyright (C) 2014-2016, A10 Networks Inc. All rights reserved.
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


import logging


LOG = logging.getLogger(__name__)

DEFAULT_HM_TRANSFORM = lambda x: "{0}".format(x.get("type"))

HTTP_TRANSFORM = lambda x: "{0} {1}".format(x.get("type"), x.get("http_method"))

HM_DISPLAY_TRANSFORMS = {
    "HTTP": HTTP_TRANSFORM,
    "HTTPS": HTTP_TRANSFORM,
}


def transform_admin_state_up(datum):
    return "UP" if datum.get("admin_state_up", False) else "DOWN"


def transform_connection_limit(datum):
    conn_limit = datum.get("connection_limit")
    return "-" if conn_limit == -1 else conn_limit


def transform_session_persistence(datum):
    sp = datum.get("session_persistence") or {}
    if "type" in sp:
        return "{0}".format(sp.get("type"))
    else:
        return "None"


def healthmonitor_summary(datum):
    hm_type = datum.get("type")
    type_transform = HM_DISPLAY_TRANSFORMS.get(hm_type, DEFAULT_HM_TRANSFORM)
    return type_transform(datum)


# This function generates links and names.
def links_from_hm_pools(datum):
    return datum["name"]


def display_health_monitor(datum):
    rv = datum.get("healthmonitor_id")
    return str(rv)
