from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app import logger_factory
from src.crosscutting import JsonSnakeToCamelSerializer, PinfluencerObjectMapper
from src.data import Base
from src.data.entities import SqlAlchemyBaseEntity
from src.domain.models import ValueEnum, CategoryEnum
from src.web.mapping import MappingRules

TEST_DEFAULT_PRODUCT_IMAGE1 = "default_product_image1.png"
TEST_DEFAULT_PRODUCT_IMAGE2 = "default_product_image2.png"
TEST_DEFAULT_PRODUCT_IMAGE3 = "default_product_image3.png"
TEST_DEFAULT_BRAND_LOGO = "default_brand_logo.png"
TEST_DEFAULT_BRAND_HEADER_IMAGE = "default_brand_header_image.png"
TEST_DEFAULT_INFLUENCER_PROFILE_IMAGE = "default_influencer_profile_image.png"


def test_mapper() -> PinfluencerObjectMapper:
    object_mapper = PinfluencerObjectMapper(logger=logger_factory())
    rules = MappingRules(mapper=object_mapper)
    rules.add_rules()
    return object_mapper



class InMemorySqliteDataManager:

    def __init__(self):
        self.__engine = create_engine('sqlite:///:memory:')
        session = sessionmaker(bind=self.__engine)
        self.__session = session()
        Base.metadata.create_all(self.__engine)

    @property
    def engine(self):
        return self.__engine

    @property
    def session(self):
        return self.__session

    def create_fake_data(self, objects):
        for object in objects:
            self.__session.add(object)
        self.session.commit()


def get_entity_dict(entity: SqlAlchemyBaseEntity) -> dict:
    dict = entity.__dict__
    dict.pop('_sa_instance_state')
    return dict


def get_as_json(status_code: int,
                body: str = "{}") -> dict:
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {"Content-Type": "application/json",
                    'Access-Control-Allow-Origin': "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "*"},
    }


class RepoEnum(Enum):
    NO_REPO = 'NO_REPO',
    STD_REPO = 'STD_REPO',
    AUTH_REPO = 'AUTH_REPO'


def get_influencer_id_event(id):
    return {'pathParameters': {'influencer_id': id}}


def get_brand_id_event(brand_id):
    return {'pathParameters': {'brand_id': brand_id}}


def get_notification_id_event(notification_id):
    return {'pathParameters': {'notification_id': notification_id}}


def get_campaign_id_event(campaign_id):
    return {'pathParameters': {'campaign_id': campaign_id}}


def get_auth_user_event(auth_id):
    return {"requestContext": {"authorizer": {"jwt": {"claims": {"username": auth_id}}}}}


def update_brand_payload():
    return {
        "first_name": "",
        "last_name": "",
        "email": "",
        "brand_name": "name",
        "brand_description": "description",
        "website": "https://website.com",
        "insta_handle": "instahandle",
        "values": [ValueEnum.VALUE7, ValueEnum.VALUE8, ValueEnum.VALUE9],
        "categories": [CategoryEnum.CATEGORY7, CategoryEnum.CATEGORY6, CategoryEnum.CATEGORY5]
    }


def update_image_payload():
    return {
        "image_bytes": "random_bytes"
    }


def create_for_auth_user_event(auth_id, payload):
    return {
        "requestContext": {"authorizer": {"jwt": {"claims": {"cognito:username": auth_id}}}},
        "body": JsonSnakeToCamelSerializer().serialize(payload)
    }
