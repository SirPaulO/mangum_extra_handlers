# Mangum extra handlers

An extra set of [Mangum](https://github.com/jordaneremieff/mangum) handlers for AWS SQS, SNS and EventBridge services. 

## Installation

```console
$ pip install mangum-extra-handlers
```


## Example

```python
from mangum_extra_handlers import EventBridgeHandler, SNSHandler, SQSHandler

...

handler = Mangum(app, lifespan="off", custom_handlers=[SNSHandler, SQSHandler, EventBridgeHandler])
```
