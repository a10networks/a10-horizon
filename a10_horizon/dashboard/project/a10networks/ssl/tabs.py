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

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from a10_horizon.dashboard.api import certificates as cert_api
import tables


LOG = LOG = logging.getLogger(__name__)


class CertificatesTab(tabs.TableTab):
    table_classes = (tables.CertificatesTable,)
    name = _("Certificates")
    slug = "certificates"
    template_name = "certificates/_certificates_tab.html"
    preload = False

    def get_certificatestable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            certificates = []
            certificates = cert_api.certificate_list(self.tab_group.request,
                                                     tenant_id=tenant_id)
        except Exception as ex:
            certificates = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve certificate list.'))
            LOG.error("Could not retrieve certificate list. ERROR=%s" % ex)
        return certificates


class CertificateBindingsTab(tabs.TableTab):
    table_classes = (tables.CertificateBindingsTable,)
    name = _("Certificate Associations")
    slug = "certificatebindings"
    template_name = "certificates/_certificatebindings_tab.html"

    def get_certificatebindingtable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            bindings = []
            bindings = cert_api.certificate_bindings_list(self.tab_group.request,
                                                          tenant_id=tenant_id)
        except Exception as ex:
            bindings = []
            exceptions.handle(self.tab_group.request, _("Unable to retrieve certificate "
                                                        "associations list."))
            LOG.error("Could not retrieve certificate associations list. ERROR=%s" % ex)

        return bindings


class A10SSLTabs(tabs.TabGroup):
    slug = "a10ssltabs"
    tabs = (CertificatesTab,
            CertificateBindingsTab
            )
    sticky = True
