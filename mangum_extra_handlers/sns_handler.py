from mangum.handlers.utils import handle_base64_response_body, handle_multi_value_headers, maybe_encode_body
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope


class SNSHandler:
    # noinspection PyUnusedLocal
    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        if (event.get("Records") and type(event.get("Records")) is list and len(event.get("Records")) == 1 and
                event.get("Records")[0].get("EventSource") and event.get("Records")[0].get("EventSource") == "aws:sns"):
            return True
        return False

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:
        self.event = event
        self.context = context
        self.config = config

    @property
    def body(self) -> bytes:
        return maybe_encode_body(
            self.event["Records"][0]["Sns"].get("Message", b""),
            is_base64=self.event.get("isBase64Encoded", False),
        )

    @property
    def scope(self) -> Scope:
        topic = self.event["Records"][0]["Sns"]["TopicArn"].split(":")[-1]
        subject = self.event["Records"][0]["Sns"]["Subject"]
        return {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": [],
            "path": f"/internal/sns/{topic}/{subject}",
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
            "aws.context": self.context,
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
