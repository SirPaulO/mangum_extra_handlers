import json

from mangum.handlers.utils import handle_base64_response_body, handle_multi_value_headers
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope, LambdaHandler


class EventBridgeHandler(LambdaHandler):

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:
        super().__init__(event, context, config)
        self.event = event
        self.context = context
        self.config = config

    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        if "source" in event and "events" in event["source"]:
            return True
        return False

    @property
    def body(self) -> bytes:
        return json.dumps(self.event).encode("utf-8")

    @property
    def scope(self) -> Scope:
        return {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": [],
            "path": "/internal/eventbridge",
            "raw_path": None,
            "root_path": "",
            "scheme": "https",
            "query_string": [],
            "server": None,
            "client": (
                "0.0.0.0",
                0,
            ),
            "asgi": {"version": "3.0", "spec_version": "2.0"},
            "aws.event": self.event,
            "aws.context": None,
        }

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
