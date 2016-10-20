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
import random

def _random_name():
    chars = []
    for n in range(1, 16):
        chars.append(chr(random.randint(65, 90)))
    return "".join(chars)

# TODO(mdurrant) - Remove the debugging crap

CERT_DATA = """-----BEGIN CERTIFICATE-----
MIID1zCCAr+gAwIBAgIJAIUmrLlxfBYIMA0GCSqGSIb3DQEBCwUAMIGBMQswCQYD
VQQGEwJVUzELMAkGA1UECAwCSUQxDjAMBgNVBAcMBUJvaXNlMRwwGgYDVQQKDBNB
MTAgTmV0d29yayBUZXN0aW5nMRUwEwYDVQQLDAxTb2Z0d2FyZSBEZXYxIDAeBgNV
BAMMF3NzbHRlc3QuYTEwbmV0d29ya3MuY29tMB4XDTE2MTAxMTIwMDYyOVoXDTI2
MTAwOTIwMDYyOVowgYExCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJJRDEOMAwGA1UE
BwwFQm9pc2UxHDAaBgNVBAoME0ExMCBOZXR3b3JrIFRlc3RpbmcxFTATBgNVBAsM
DFNvZnR3YXJlIERldjEgMB4GA1UEAwwXc3NsdGVzdC5hMTBuZXR3b3Jrcy5jb20w
ggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDbnD5CiARaiDAjd53AGwtO
DG0fbPOldi8/anCyZWA2/lPlbBvSGBZtNjAtG+a6jGQhxlp27K3yheuF0jZeBpFk
adBMSUQYCYfNeMFn2n8JThO8k1IfAheKxzAzjq454ieAOjTuUkVLHWV74mkfmE7e
qJWEen3idoJahmofWKLFXB3g/r2vyjVAllka1r37N6YNbO3EPE3SVGdHylQSlXI8
ajenHgiSf+luhzsfx5/o+cuSUhmFD5i1J0AHdtcgdd+OXR/11dG4fy3oir+8cbaV
dwaXP65ra5W7b3nOeI4JO1N7Aa1z8Mtbb1J16QRHJT/ekCh+OF5HNrkmXZLD0jRL
AgMBAAGjUDBOMB0GA1UdDgQWBBRmg1gbMqCOxj5atETfBYp4e/pyLzAfBgNVHSME
GDAWgBRmg1gbMqCOxj5atETfBYp4e/pyLzAMBgNVHRMEBTADAQH/MA0GCSqGSIb3
DQEBCwUAA4IBAQA8XsLizv4KiO0PGK+k7zF5xJ9ogVZdkjY+CgXlop0xTq+Kt7n1
+6EPorS7HNYiltC4pr5OjcMhDtKORloV0ATSa5K27dyzYYw6v1cfVOiivixyT6dY
hm9EZs+gYt8kVo1mAfb0g6zqRJy3gkMVkhsb4DlxPRNcKMX1bLrfisrRfc6yDH6D
dZBK63BSYh7H8wHh1CE6kBjdNOFDL4nJIRup/mtCZETU7z/FFvnEqaBDkIKVQ4dk
LyUPKyQcM6tFc6WjHTx/YOuih4gaupzJDCMWjyWrrNxNIaTZziRSuCggLs4b3LQD
j84tU5/SsueWoIXdCcogq9Szn/UjfJGi9n1s
-----END CERTIFICATE-----"""

KEY_DATA = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDbnD5CiARaiDAj
d53AGwtODG0fbPOldi8/anCyZWA2/lPlbBvSGBZtNjAtG+a6jGQhxlp27K3yheuF
0jZeBpFkadBMSUQYCYfNeMFn2n8JThO8k1IfAheKxzAzjq454ieAOjTuUkVLHWV7
4mkfmE7eqJWEen3idoJahmofWKLFXB3g/r2vyjVAllka1r37N6YNbO3EPE3SVGdH
ylQSlXI8ajenHgiSf+luhzsfx5/o+cuSUhmFD5i1J0AHdtcgdd+OXR/11dG4fy3o
ir+8cbaVdwaXP65ra5W7b3nOeI4JO1N7Aa1z8Mtbb1J16QRHJT/ekCh+OF5HNrkm
XZLD0jRLAgMBAAECggEAFUj/f9NPGLc6czWUxJnabqYlrXYR52edDLh0U9YfjTT5
TLM9vw82nT8zTCv4IPyad+uRuRUXhvoT6dSGEHbygJkA52PyhaHm17Nsi3RR+8Tl
hNGClB7PyVOlCFo76MBSs8rwdmji7nTa8TbwmW9ZtZsBYuW8bcauu7drcb5ViGtH
I1mJycZ2RxDvpXvWpRClwfFiJTEpBgxYo8psaFkUFQqht2j3hD7kyuzpxO9xpjsh
Wl2Eee0p8b2QVmiCT/LgqB8d9Z3VCdew4r2Un99PfO7q4OFcWwJ3s1Y0apQQ914E
MoTgITBM7COhaVAnKPGa/xvJTqSZ0wEoYI5YXK2EAQKBgQD/U3xhTJGisNdMCsuo
WSXRmHby9GNp+Ut2PzhbxY5HovDGNauiIlkVFelUQ18XGE0tlYKiFTv15XbKNatB
qr7uATTrV1f8IWrlUOwhrrTQyJPay6m0MvbfX7Y7uBEi4t1bHaU8/JYR6iYvG2pX
cuArwmVoStJRedCOmCIYGW106wKBgQDcMKAjgim9OGcVL9J+tHnbchf9xWWJR7r4
HwQZE2qddMVC7sJnMf0yGLWSUBuIlh+8t9vD31E5GjAN1z4DYs4iHZwH70QDtYSy
keC9G8QEQk/VZTVdBtnXp+YRj++ol+Y1mkE/2+530A3pcQBEpNfxQpV0VajFkFeF
aI+X4kHmIQKBgQDjFqzsmT56tdB3eK6UZ93EIlfBVO3KxoiAflAxB2+5dUmy8O9b
gDM9FsT1RgqgLuQN5AlRAZPX66QQy1UrTaMNapNXsdK2lD5QAP5UIt/9RjiDBFtG
w4FhQO6DBP5wydhY/vAFYx5ShrA5e6fEaY7KPNcWwF15S9/bw6GnT45TywKBgGrw
PsYgEE9y1jWm/S9GTaxzdA1u0kpjCP46ag4XrP792FQSi139HEA5We3OdCDY8F8C
WHx/t/3opxAByn9wfDZ7dO0xmjHG9cSYLrMJiiCbaBR2y/z7N8+SHp3G7xlNdKPx
3+C42s9bv3XxyLSN7saglN9kPsx8ttT3HE4it+ihAoGBANvIAPjKySNPcbz6eeYE
pLLzK0l5oRNPGnqOj6N5Njy5IWz/T0MRB1Mh/w0zNk9EQbdhzV5Lm71cuNOZb93W
5vxpPBxWyAWBjlaPiPxz0AmjKPrXsRekyTsBe8HJ1Bk8/qSY8k0Gk8yKgPm2Je3L
Rv4a8yRehRRjWFxwExTtwFwh
-----END PRIVATE KEY-----"""
