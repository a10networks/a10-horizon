# Copyright (C) 2016, A10 Networks Inc. All rights reserved.
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


import horizon
import logging

from openstack_dashboard.api import neutron as neutron_api

LOG = logging.getLogger(__name__)


class NeutronExtensionPanelBase(horizon.Panel):
    """Name of Neutron extension(s) that enables the panel.
    """
    REQUIRED_EXTENSIONS = []

    def allowed(self, context):
        exts = []

        if len(self.REQUIRED_EXTENSIONS) > 0:
            # Ensure all of the named extensions are present.  Else, return false.
            try:
                exts = [x["alias"] for x in neutron_api.list_extensions(context.request)]
                missing_exts = set(self.REQUIRED_EXTENSIONS) - set(exts)

                if len(missing_exts) > 0:
                    msg = "\n\n\n"
                    msg += "-------------- A10 NETWORKS SUPPORT INFORMATION --------------\n"
                    msg += "The following extensions are required to load this plugin:" + "\n\n"
                    msg += "\n".join(missing_exts)
                    msg += "\n\nPlease contact A10 Account Team to enable.\n"
                    msg += "--------------------------------------------------------------\n"
                    LOG.error(msg)
                    return False
                else:
                    return True

            except Exception as ex:
                LOG.error("There was a problem retrieving the extension list."
                          "See exception for details.")
                LOG.exception(ex)
            return False
        # explicit else - we'd fall through to this.
        else:
            return True
