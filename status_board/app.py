import yaml
import json
import logging

import web

log = logging.getLogger()
log.setLevel(logging.INFO)


def response(status_code, obj=None, headers={}, body=None):
    logging.debug(
        yaml.dump(
            {"response": {"statusCode": status_code, "obj": obj, "headers": headers}}
        )
    )
    if body:
        if obj:
            raise ValueError("Cannot have both body and obj in response")
    elif obj:
        body = json.dumps(obj) + "\n"
    else:
        body = "\n"

    return {"statusCode": status_code, "body": body, "headers": headers}


def success(**obj):
    return response(200, obj)


def fail(status_code, *msg, **obj):
    return response(status_code, {"message": " ".join(msg), **obj})


def redirect(location, status_code=302):
    return response(status_code, headers={"Location": location})


def lambda_handler(event, context):
    try:
        log.debug(yaml.dump({"event": event}))
        return response(
            200, body=web.status_board(), headers={"content-type": "text/html"}
        )
    except:
        log.exception("Error in handler")

    return fail(500, "Internal error. Check CloudWatch logs")
