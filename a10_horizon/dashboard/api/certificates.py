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

from __future__ import absolute_import

# from django.utils.datastructures import SortedDict
# from django.utils.translation import ugettext_lazy as _
import logging
from horizon import messages

from openstack_dashboard.api import neutron

LOG = logging.getLogger(__name__)
neutronclient = neutron.neutronclient

CERT_ATTRIBUTE = "a10_certificate"
CERT_PLURAL = CERT_ATTRIBUTE + "%s" % "s"


def list_certificates(request, **kwargs):
    # TODO(mdurrant) Fix this terribadness.
    # 1. kwargs={} should result IN THE SAME RETURN TYPE
    # 2. kwargs=WhoKnows ...?
    # 3. kwargs=None ... ?
    # Return types as follows
    # 1. Return type: An iterator
    # 2. Return type: A listerator? Good question.
    # 3. Return type: Always a list.

    rv = list(neutronclient(request).list_a10_certificates(kwargs))[0]
    return rv.get("a10_certificates", [])


def get_certificate(request, id, **kwargs):
    rv = neutronclient(request).show_a10_certificate(id, **kwargs)
    return rv.get("a10_certificate", {})


def create_certificate(request, certificate):
    rv = neutronclient(request).create_a10_certificate(certificate).get("a10_certificate", {})
    return rv


def delete_certificate(request, id):
    neutronclient(request).delete_a10_certificate(id)


def update_certificate(request, id, **kwargs):
    body = {"a10_certificate": kwargs}
    rv = neutronclient(request).update_a10_certificate(id, body).get("a10_certificate", {})
    return rv


def create_binding(request, listener_id, cert_id):
    body = {"a10_certificate_binding": {
        "listener_id": listener_id,
        "certificate_id": cert_id
    }}
    rv = neutronclient(request).create_a10_certificate_binding(
        body).get("a10_certificate_binding", {})
    return rv
