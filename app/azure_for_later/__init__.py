# manually trigger with
# http://osca-sub-bot.azurewebsites.net/api/app

import logging
import azure.functions as func
import app.steps.reader.reader
from app.azure_for_later import runApp
# import steps.emailSender


def main(req: func.HttpRequest) -> func.HttpResponse:
    runApp()

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )