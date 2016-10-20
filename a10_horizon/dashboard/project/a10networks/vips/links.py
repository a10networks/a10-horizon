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

from django.core.urlresolvers import reverse_lazy
import logging

LOG = logging.getLogger(__name__)
URL_PREFIX = "horizon:project:a10vips:"


def link_loadbalancer_detail_by_id(datum):
    return reverse_lazy(URL_PREFIX + "lbdetail", kwargs={"id": datum["id"]})


def link_listener_detail_by_id(datum):
    return reverse_lazy(URL_PREFIX + "listenerdetail", kwargs={"id": datum["id"]})


def link_member_detail_by_id(datum):
    return reverse_lazy(URL_PREFIX + "memberdetail",
                        kwargs={"id": datum["id"], "pool_id": datum["pool_id"]})


def link_pool_detail_by_id(datum):
    return reverse_lazy(URL_PREFIX + "pooldetail", kwargs={"id": datum["id"]})


def link_pool_detail_from_hm(datum):
    pools = datum.get("pools")
    # TODO(mdurrant) - Move this to a template.
    if len(pools) > 0:
        pool = pools[0]

    return reverse_lazy(URL_PREFIX + "pooldetail", kwargs={"id": pool.get("id")})


def link_hm_detail_from_pool(datum):
    hmid = datum.get("healthmonitor_id", None)
    if hmid:
        return reverse_lazy(URL_PREFIX + "monitordetail", kwargs={"id": hmid})
    else:
        return None


def link_hm_detail_by_id(datum):
    hmid = datum.get("id", None)
    if hmid:
        return reverse_lazy(URL_PREFIX + "monitordetail", kwargs={"id": hmid})
    else:
        return None


def link_certificate_detail_by_id(datum):
    certid = datum.get("id", None)
    if certid:
        return reverse_lazy(URL_PREFIX + "certificatedetail", kwargs={"id": certid})
    else:
        return None
