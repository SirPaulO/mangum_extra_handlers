from mangum.handlers.utils import handle_base64_response_body, handle_multi_value_headers, maybe_encode_body
from mangum.types import LambdaConfig, LambdaContext, LambdaEvent, Response, Scope


class SNSHandler:

    def __init__(self, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> None:
        super().__init__(event, context, config)
        self.event = event
        self.context = context
        self.config = config

    @classmethod
    @classmethod
    def infer(cls, event: LambdaEvent, context: LambdaContext, config: LambdaConfig) -> bool:
        records = event.get("Records")
        if type(records) is not list or len(records) < 1:
            return False

        source = records[0].get("eventSource")
        if type(source) is str and source == "aws:sns":
            return True

        return False

    @property
    def body(self) -> bytes:
        return json.dumps(self.event.get("Records")).encode("utf-8")

    @property
    def scope(self) -> Scope:
        return {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "headers": [],
            "path": "/internal/sns",
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
