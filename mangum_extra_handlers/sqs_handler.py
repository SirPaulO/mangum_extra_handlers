from mangum.handlers.utils import handle_base64_response_body, handle_multi_value_headers, maybe_encode_body
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope, LambdaHandler


class SQSHandler(LambdaHandler):

    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        if (event.get("Records") and type(event.get("Records")) is list and len(event.get("Records")) == 1 and
                event.get("Records")[0].get("eventSource") and event.get("Records")[0].get("eventSource") == "aws:sqs"):
            return True
        return False

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:  # noqa
        self.event = event
        self.context = context
        self.config = config

    @property
    def body(self) -> bytes:
        return maybe_encode_body(
            self.event["Records"][0].get("body", b""),
            is_base64=self.event.get("isBase64Encoded", False),
        )

    @property
    def scope(self) -> Scope:
        caller = self.event["Records"][0]["eventSourceARN"].split(":")[-1]
        return {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": [],
            "path": f"/internal/sqs/{caller}",
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
