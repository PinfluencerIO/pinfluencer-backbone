import json


class PinfluencerResponse:
    def __init__(self, status_code=200, body=None):
        if body is None:
            body = {}

        self.status_code = status_code
        self.body = body

    def is_ok(self):
        return 200 <= self.status_code < 300

    def as_json(self):
        return {
            'statusCode': self.status_code,
            'body': json.dumps(self.body, default=str),
            'headers': {'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': '*',
                        'Access-Control-Allow-Methods': '*'},
        }

    @staticmethod
    def as_500_error(message="Unexpected server error. Please try later."):
        return PinfluencerResponse(500, {"message": message})

    @staticmethod
    def as_400_error(message='Client error, please check request.'):
        return PinfluencerResponse(400, {"message": message})
