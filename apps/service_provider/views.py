from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from saml2 import BINDING_HTTP_POST

from apps.service_provider.saml import saml_client


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

