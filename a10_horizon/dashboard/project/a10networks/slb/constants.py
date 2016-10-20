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

OP_DICT = {
    ">": "greater than",
    "<": "less than",
    ">=": "greater than or equal to",
    "<=": "less than or equal to",
}

AGG_DICT = {
    "avg": "average",
    "sum": "sum",
    "min": "minimum",
    "max": "maximum"
}

UNIT_DICT = {
    "count": "",
    "percentage": "%",
    "bytes": "bytes",
}

MEASUREMENTS = [
    "connections",
    "cpu",
    "interface",
    "memory"
]

VALID_MEASUREMENT_UNITS = {
    "connections": ["count"],
    "cpu": ["percentage"],
    "interface": ["percentage", "count"],
    "memory": ["bytes", "percentage"],
}
