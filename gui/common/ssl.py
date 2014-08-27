#+
# Copyright 2014 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################
import logging
import re

from OpenSSL import crypto

log = logging.getLogger('common.ssl')

def generate_key(key_length):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, key_length)
    return k


def create_certificate(cert_info):
    cert = crypto.X509()
    cert.get_subject().C = cert_info['country']
    cert.get_subject().ST = cert_info['state']
    cert.get_subject().L = cert_info['city']
    cert.get_subject().O = cert_info['organization']
    cert.get_subject().CN = cert_info['common']
    cert.get_subject().emailAddress = cert_info['email']

    serial = cert_info.get('serial')
    if serial != None:
        cert.set_serial_number(serial)

    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(cert_info['lifetime'] * (60*60*24))

    cert.set_issuer(cert.get_subject())
    return cert


def sign_certificate(cert, key, digest_algorithm):
    cert.sign(key, str(digest_algorithm))


def create_self_signed_certificate(cert_info):
    key = generate_key(cert_info['key_length'])

    cert = create_certificate(cert_info)
    cert.set_pubkey(key)

    sign_certificate(cert, key, cert_info['digest_algorithm'])

    return (cert, key)


def create_certificate_signing_request(cert_info):
    key = generate_key(cert_info['key_length'])

    req = crypto.X509Req()
    req.get_subject().C = cert_info['country']
    req.get_subject().ST = cert_info['state']
    req.get_subject().L = cert_info['city']
    req.get_subject().O = cert_info['organization']
    req.get_subject().CN = cert_info['common']
    req.get_subject().emailAddress = cert_info['email']

    req.set_pubkey(key)
    sign_certificate(req, key, cert_info['digest_algorithm'])

    return (req, key)


def load_certificate(buf):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, buf)
    
    cert_info = {}
    cert_info['country'] = cert.get_subject().C
    cert_info['state'] = cert.get_subject().ST
    cert_info['city'] = cert.get_subject().L
    cert_info['organization'] = cert.get_subject().O
    cert_info['common'] = cert.get_subject().CN
    cert_info['email'] = cert.get_subject().emailAddress

    signature_algorithm = cert.get_signature_algorithm()
    m = re.match('^(.+)[Ww]ith', signature_algorithm)
    if m:
        cert_info['digest_algorithm'] = m.group(1).upper()

    return cert_info 


def export_certificate(buf):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, buf)
    return crypto.dump_certificate(crypto.FILETYPE_PEM, cert)


def export_privatekey(buf):
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, buf)
    return crypto.dump_privatekey(crypto.FILETYPE_PEM, key)