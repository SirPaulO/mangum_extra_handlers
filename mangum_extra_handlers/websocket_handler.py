import json

from mangum.handlers.utils import handle_base64_response_body, handle_multi_value_headers, maybe_encode_body
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope


class WebSocketHandler:
    # noinspection PyUnusedLocal
    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        if "requestContext" in event and "routeKey" in event["requestContext"]:
            return True
        return False

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:
        self.event = event
        self.context = context
        self.config = config

    @property
    def body(self) -> bytes:
        body = self.event.get("body", b"")
        if type(body) is dict:
            body = json.dumps(body)
        return maybe_encode_body(
            body,
            is_base64=self.event.get("isBase64Encoded", False),
        )

    @property
    def scope(self) -> Scope:
        route_key = self.event["requestContext"]["routeKey"]
        route_key = route_key.replace("$", "")
        connection_id = self.event["requestContext"]["connectionId"]
        formated_headers = []
        if "headers" in self.event:
            headers = self.event["headers"]
            allowed_headers = ["white-listed-header", "another-white-listed-header"]
            for key, value in headers.items():
                if key not in allowed_headers:
                    continue
                bytes_key = bytes(key.lower(), "utf-8")
                bytes_value = bytes(value, "utf-8")
                formated_headers.append([bytes_key, bytes_value])

        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": formated_headers,
            "path": f"/internal/websocket/{route_key}/{connection_id}",
            "raw_path": None,
            "root_path": "",
            "scheme": "https",
            "query_string": [],
            "server": None,  # tuple of (host, port)
            "client": (
                "0.0.0.0",
                0,
            ),
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "aws.event": self.event,
            "aws.context": None,
        }

        return scope

    def __call__(self, response: Response) -> dict:
        finalized_headers, multi_value_headers = handle_multi_value_headers(response["headers"])
        finalized_body, is_base64_encoded = handle_base64_response_body(response["body"], finalized_headers, [])

        return {
            "statusCode": response["status"],
            "headers": finalized_headers,
            "multiValueHeaders": multi_value_headers,
            "body": finalized_body,
            "isBase64Encoded": is_base64_encoded,
        }
