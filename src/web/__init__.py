from dataclasses import dataclass, field
from typing import Union, Callable

from src.types import Serializer

BRAND_ID_PATH_KEY = 'brand_id'
INFLUENCER_ID_PATH_KEY = 'influencer_id'


class PinfluencerResponse:
    def __init__(self, status_code: int = 200, body: Union[dict, list] = {}) -> None:
        self.status_code = status_code
        self.body = body

    def is_ok(self):
        return 200 <= self.status_code < 300

    def as_json(self, serializer: Serializer) -> dict:
        return {
            "statusCode": self.status_code,
            "body": serializer.serialize(self.body),
            "headers": {"Content-Type": "application/json",
                        'Access-Control-Allow-Origin': "*",
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Allow-Methods": "*"},
        }

    @staticmethod
    def as_500_error(message="unexpected server error, please try later :("):
        return PinfluencerResponse(500, {"message": message})

    @staticmethod
    def as_400_error(message='Client error, please check request.'):
        return PinfluencerResponse(400, {"message": message})


def get_cognito_user(event):
    return event['requestContext']['authorizer']['jwt']['claims']['cognito:username']


@dataclass
class PinfluencerContext:
    response: PinfluencerResponse = None,
    short_circuit: bool = False,
    event: Union[list, dict] = field(default_factory=dict),
    auth_user_id: str = "",
    body: dict = field(default_factory=dict)


PinfluencerAction = Callable[[PinfluencerContext], None]


@dataclass
class Route:
    action: PinfluencerAction
    after_hooks: list[PinfluencerAction] = field(default_factory=list)