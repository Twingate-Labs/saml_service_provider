from dataclasses import dataclass

from saml2 import BINDING_HTTP_POST, md, BINDING_HTTP_REDIRECT, samlp, xmldsig
from saml2.client import Saml2Client
from saml2.config import Config
from saml2.mdstore import InMemoryMetaData
from saml2.sigver import get_xmlsec_binary


@dataclass
class IdPConfig:
    entity_id: str
    single_sign_on_url: str
    x509_cert: str

    def __hash__(self):
        return hash(self.entity_id)


if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"])
else:
    xmlsec_path = "/usr/bin/xmlsec1"


def saml_client():
    saml_settings = {
        # Currently xmlsec1 binaries are used for all the signing and encryption stuff.This option defines where the binary is situated.
        "xmlsec_binary": xmlsec_path,
        # The SP ID. It is recommended that the entityid should point to a real webpage where the metadata for the entity can be found.
        "entityid": "http://localhost:8000/sample_sp",
        # Indicates that attributes that are not recognized (they are not configured in attribute-mapping), will not be discarded.
        "allow_unknown_attributes": True,
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        ##as mentioned in the sequence diagram we can use either redirect or post here.
                        ("http://localhost:8000/saml2/acs/", BINDING_HTTP_POST),
                    ]
                },
                # Don't verify that the incoming requests originate from us via the built-in cache for authn request ids in pysaml2
                "allow_unsolicited": True,
                # Don't sign authn requests, since signed requests only make sense in a situation where you control both the SP and IdP
                "authn_requests_signed": False,
                # Assertion must be signed
                "want_assertions_signed": True,
                # Response signing is optional.
                "want_response_signed": False,
            }
        },
        "metadata": [
            {
                "class": "apps.service_provider.saml.MetaDataIdP",
                "metadata": [
                    (
                        IdPConfig(
                            entity_id="jumpcloud/twingate/sample-sp",
                            single_sign_on_url="https://sso.jumpcloud.com/saml2/saml2",
                            x509_cert="<change_it>"
                        ),
                    )
                ],
            }
        ],
    }

    config = Config()
    config.load(saml_settings)

    return Saml2Client(config=config)


class MetaDataIdP(InMemoryMetaData):
    def __init__(self, attrc, metadata: IdPConfig):
        super(MetaDataIdP, self).__init__(attrc, metadata)
        self.metadata = metadata

    def load(self, *args, **kwargs):
        idpsso_descriptor = md.IDPSSODescriptor()
        idpsso_descriptor.protocol_support_enumeration = samlp.NAMESPACE
        idpsso_descriptor.single_sign_on_service = [
            md.SingleSignOnService(
                binding=BINDING_HTTP_REDIRECT, location=self.metadata.single_sign_on_url
            )
        ]
        idpsso_descriptor.key_descriptor = [
            md.KeyDescriptor(
                use="signing",
                key_info=xmldsig.KeyInfo(
                    x509_data=[
                        xmldsig.X509Data(
                            x509_certificate=xmldsig.X509Certificate(
                                text=self.metadata.x509_cert
                            )
                        )
                    ]
                ),
            )
        ]

        entity_descriptor = md.EntityDescriptor()
        entity_descriptor.entity_id = self.metadata.entity_id
        entity_descriptor.idpsso_descriptor = [idpsso_descriptor]

        self.do_entity_descriptor(entity_descriptor)

if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"])
else:
    xmlsec_path = "/usr/bin/xmlsec1"