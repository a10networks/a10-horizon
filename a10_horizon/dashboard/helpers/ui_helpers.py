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

LOG = logging.getLogger(__name__)


def switchable_field(slug):
    return {
        "class": "switchable",
        "data-slug": slug
    }


def readonly(obj=None):
    # if object specified, make it read only
    rv = {"readonly": "readonly" }
    if obj:
        obj.update(rv)
        return obj
    else:
    # return the readonly json attribute
        return rv
