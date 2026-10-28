from http import HTTPStatus
from typing import override

from django.views.decorators.debug import sensitive_variables
from dmr import Body, modify

from api_auth.controllers import email
from api_auth.schemas.verification import EmailConfirmPost, EmailResendPost
from rudi_auth.services.account import confirm_email, resend_verification

########################################################################################

# same contract as the template's endpoints (schemas, auth, throttling); only
# the services change, to carry the consequences a verified persona implies


class EmailConfirmController(email.EmailConfirmController):
    @override
    @sensitive_variables()
    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def post(self, parsed_body: Body[EmailConfirmPost]) -> None:
        await confirm_email(parsed_body.token)


########################################################################################


class EmailResendController(email.EmailResendController):
    @override
    @modify(status_code=HTTPStatus.ACCEPTED)
    async def post(self, parsed_body: Body[EmailResendPost]) -> None:
        await resend_verification(parsed_body.email)
