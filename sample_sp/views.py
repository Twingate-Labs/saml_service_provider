from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from saml2 import BINDING_HTTP_POST, md, BINDING_HTTP_REDIRECT, samlp, xmldsig
from saml2.mdstore import InMemoryMetaData
from saml2.sigver import get_xmlsec_binary

from sample_sp.saml import saml_client, IdPConfig


def login(request):
    client = saml_client()
    request_id, info = client.prepare_for_authenticate()
    redirect_url = dict(info["headers"])["Location"]

    return redirect(redirect_url)


@csrf_exempt
def assertion_consumer_service(request):
    client = saml_client()
    authn_response = client.parse_authn_request_response(
        request.POST["SAMLResponse"], BINDING_HTTP_POST
    )
    session_info = authn_response.session_info()
    session_info["name_id"] = str(session_info["name_id"])

    return JsonResponse(session_info)


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