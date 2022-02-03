import json
import uuid
from unittest import TestCase
from unittest.mock import Mock, MagicMock

from callee import Captor

from src.data import AlreadyExistsException
from src.domain.models import Brand, ValueEnum, CategoryEnum
from src.domain.validation import BrandValidator
from src.typing import BrandRepository
from src.web.controllers import BrandController
from src.web.validation import valid_uuid
from tests import brand_dto_generator


def get_brand_id_event(brand_id):
    return {'pathParameters': {'brand_id': brand_id}}


def get_auth_user_event(auth_id):
    return {"requestContext": {"authorizer": {"jwt": {"claims": {"cognito:username": auth_id}}}}}


def update_brand_payload():
    return {
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email@gmail.com",
        "name": "name",
        "description": "description",
        "website": "https://website.com",
        "instahandle": "instahandle",
        "values": ["VALUE7", "VALUE8", "VALUE9"],
        "categories": ["CATEGORY7", "CATEGORY6", "CATEGORY5"]
    }


def update_brand_return_dto():
    return Brand(first_name="first_name",
                 last_name="last_name",
                 email="email@gmail.com",
                 name="name",
                 description="description",
                 website="https://website.com",
                 instahandle="instahandle",
                 values=[ValueEnum.VALUE7, ValueEnum.VALUE8, ValueEnum.VALUE9],
                 categories=[CategoryEnum.CATEGORY7, CategoryEnum.CATEGORY6, CategoryEnum.CATEGORY5])


def create_brand_for_auth_user_event(auth_id, payload):
    return {
        "requestContext": {"authorizer": {"jwt": {"claims": {"cognito:username": auth_id}}}},
        "body": json.dumps(payload)
    }


class TestBrandController(TestCase):

    def setUp(self):
        self.__brand_repository: BrandRepository = Mock()
        self.__brand_validator = BrandValidator()
        self.__sut = BrandController(brand_repository=self.__brand_repository,
                                     brand_validator=self.__brand_validator)

    def test_get_by_id(self):
        brand = brand_dto_generator(num=1)
        self.__brand_repository.load_by_id = MagicMock(return_value=brand)
        pinfluencer_response = self.__sut.get_by_id(get_brand_id_event(brand.id))
        self.__brand_repository.load_by_id.assert_called_once_with(id_=brand.id)
        assert pinfluencer_response.body == brand.__dict__
        assert pinfluencer_response.is_ok() is True

    def test_get_by_id_when_not_found(self):
        self.__brand_repository.load_by_id = MagicMock(return_value=None)
        field = str(uuid.uuid4())
        pinfluencer_response = self.__sut.get_by_id(get_brand_id_event(field))
        self.__brand_repository.load_by_id.assert_called_once_with(id_=field)
        assert pinfluencer_response.body == {}
        assert pinfluencer_response.status_code == 404

    def test_get_by_id_when_invalid_uuid(self):
        self.__brand_repository.load_by_id = MagicMock(return_value=None)
        field = "12345"
        pinfluencer_response = self.__sut.get_by_id(get_brand_id_event(field))
        self.__brand_repository.load_by_id.assert_not_called()
        assert pinfluencer_response.body == {}
        assert pinfluencer_response.status_code == 400

    def test_get_all(self):
        expected_brands = [
            brand_dto_generator(num=1),
            brand_dto_generator(num=2),
            brand_dto_generator(num=3),
            brand_dto_generator(num=4)
        ]
        self.__brand_repository.load_collection = MagicMock(return_value=expected_brands)
        pinfluencer_response = self.__sut.get_all({})
        self.__brand_repository.load_collection.assert_called_once()
        assert pinfluencer_response.body == list(map(lambda x: x.__dict__, expected_brands))
        assert pinfluencer_response.status_code == 200

    def test_get(self):
        expected_brand = brand_dto_generator(num=1)
        self.__brand_repository.load_for_auth_user = MagicMock(return_value=expected_brand)
        auth_id = "1234brand1"
        response = self.__sut.get(get_auth_user_event(auth_id))
        self.__brand_repository.load_for_auth_user.assert_called_once_with(auth_user_id=auth_id)
        assert response.body == expected_brand.__dict__
        assert response.status_code == 200

    def test_get_when_not_found(self):
        self.__brand_repository.load_for_auth_user = MagicMock(return_value=None)
        auth_id = "1234brand1"
        response = self.__sut.get(get_auth_user_event(auth_id))
        self.__brand_repository.load_for_auth_user.assert_called_once_with(auth_user_id=auth_id)
        assert response.body == {}
        assert response.status_code == 404

    def test_create(self):
        expected_payload = update_brand_payload()
        auth_id = "1234brand1"
        event = create_brand_for_auth_user_event(auth_id=auth_id, payload=update_brand_payload())
        self.__brand_repository.write_new_for_auth_user = MagicMock()
        response = self.__sut.create(event=event)
        payload_captor = Captor()
        self.__brand_repository.write_new_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                                payload=payload_captor)
        actual_payload = payload_captor.arg
        assert valid_uuid(actual_payload.id)
        assert actual_payload.first_name == expected_payload['first_name']
        assert actual_payload.last_name == expected_payload['last_name']
        assert actual_payload.email == expected_payload['email']
        assert actual_payload.name == expected_payload['name']
        assert actual_payload.description == expected_payload['description']
        assert actual_payload.website == expected_payload['website']
        assert list(map(lambda x: x.name, actual_payload.values)) == expected_payload['values']
        assert list(map(lambda x: x.name, actual_payload.categories)) == expected_payload['categories']
        assert response.status_code == 201
        assert response.body == actual_payload.__dict__

    def test_create_when_exists(self):
        auth_id = "1234brand1"
        event = create_brand_for_auth_user_event(auth_id=auth_id, payload=update_brand_payload())
        self.__brand_repository.write_new_for_auth_user = MagicMock(side_effect=AlreadyExistsException())

        response = self.__sut.create(event=event)
        assert response.status_code == 400
        assert response.body == {}

    def test_create_when_invalid_payload(self):
        auth_id = "1234brand1"
        payload = update_brand_payload()
        payload['name'] = 120
        event = create_brand_for_auth_user_event(auth_id=auth_id, payload=payload)

        response = self.__sut.create(event=event)
        assert response.status_code == 400
        assert response.body == {}

    def test_update(self):
        expected_payload = update_brand_payload()
        expected_payload_dto = update_brand_return_dto()
        auth_id = "1234brand1"
        event = create_brand_for_auth_user_event(auth_id=auth_id, payload=update_brand_payload())
        self.__brand_repository.update_for_auth_user = MagicMock(return_value=expected_payload_dto)
        response = self.__sut.update(event=event)
        payload_captor = Captor()
        self.__brand_repository.update_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                             payload=payload_captor)
        actual_payload = payload_captor.arg
        assert valid_uuid(actual_payload.id)
        assert actual_payload.first_name == expected_payload['first_name']
        assert actual_payload.last_name == expected_payload['last_name']
        assert actual_payload.email == expected_payload['email']
        assert actual_payload.name == expected_payload['name']
        assert actual_payload.description == expected_payload['description']
        assert actual_payload.website == expected_payload['website']
        assert list(map(lambda x: x.name, actual_payload.values)) == expected_payload['values']
        assert list(map(lambda x: x.name, actual_payload.categories)) == expected_payload['categories']
        assert response.status_code == 200
        assert response.body == expected_payload_dto.__dict__


def assert_brand_updatable_fields_are_equal(brand1, brand2):
    assert brand1['first_name'] == brand2['first_name']
    assert brand1['last_name'] == brand2['last_name']
    assert brand1['email'] == brand2['email']
    assert brand1['name'] == brand2['name']
    assert brand1['description'] == brand2['description']
    assert brand1['website'] == brand2['website']
