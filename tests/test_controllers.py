import uuid
from unittest import TestCase
from unittest.mock import Mock, MagicMock, call

from callee import Captor

from src.crosscutting import JsonCamelToSnakeCaseDeserializer
from src.domain.models import Influencer
from src.domain.validation import BrandValidator, InfluencerValidator
from src.exceptions import AlreadyExistsException, NotFoundException
from src.types import BrandRepository, InfluencerRepository, AuthUserRepository
from src.web import PinfluencerContext, PinfluencerResponse
from src.web.controllers import BrandController, InfluencerController
from src.web.validation import valid_uuid
from tests import brand_dto_generator, assert_brand_updatable_fields_are_equal, TEST_DEFAULT_BRAND_LOGO, \
    TEST_DEFAULT_BRAND_HEADER_IMAGE, influencer_dto_generator, RepoEnum, user_dto_generator, \
    assert_brand_creatable_generated_fields_are_equal, TEST_DEFAULT_INFLUENCER_PROFILE_IMAGE, \
    assert_influencer_creatable_generated_fields_are_equal, assert_influencer_update_fields_are_equal, \
    get_influencer_id_event, get_brand_id_event, get_auth_user_event, update_brand_payload, update_user_dto, \
    create_brand_dto, update_image_payload, update_brand_return_dto, update_brand_expected_dto, \
    create_for_auth_user_event, create_influencer_dto, update_influencer_payload


class TestInfluencerController(TestCase):

    def setUp(self):
        self.__influencer_repository: InfluencerRepository = Mock()
        self.__auth_user_repo: AuthUserRepository = Mock()
        self.__sut = InfluencerController(influencer_repository=self.__influencer_repository,
                                          deserializer=JsonCamelToSnakeCaseDeserializer(),
                                          auth_user_repository=self.__auth_user_repo,
                                          influencer_validator=InfluencerValidator())

    def test_get_by_id(self):
        auth_user = user_dto_generator(num=1)
        influencer_in_db = influencer_dto_generator(num=1, repo=RepoEnum.STD_REPO)
        influencer = influencer_dto_generator(num=1)
        influencer.id = influencer_in_db.id
        influencer.created = influencer_in_db.created
        self.__influencer_repository.load_by_id = MagicMock(return_value=influencer_in_db)
        self.__auth_user_repo.get_by_id = MagicMock(return_value=auth_user)
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_by_id(PinfluencerContext(response=pinfluencer_response,
                                                event=get_influencer_id_event(influencer.id)))
        assert pinfluencer_response.body == influencer.__dict__

    def test_get(self):
        expected_influencer = influencer_dto_generator(num=1)
        db_influencer = influencer_dto_generator(num=1, repo=RepoEnum.STD_REPO)
        expected_influencer.id = db_influencer.id
        expected_influencer.created = db_influencer.created
        auth_user = user_dto_generator(num=1)
        self.__influencer_repository.load_for_auth_user = MagicMock(return_value=db_influencer)
        self.__auth_user_repo.get_by_id = MagicMock(return_value=auth_user)
        auth_id = "12341"
        response = PinfluencerResponse()
        self.__sut.get(PinfluencerContext(response=response,
                                          event=get_auth_user_event(auth_id)))
        assert response.body == expected_influencer.__dict__
        assert response.status_code == 200

    def test_get_all(self):
        influencers_from_db = [
            influencer_dto_generator(num=1, repo=RepoEnum.STD_REPO),
            influencer_dto_generator(num=2, repo=RepoEnum.STD_REPO),
            influencer_dto_generator(num=3, repo=RepoEnum.STD_REPO),
            influencer_dto_generator(num=4, repo=RepoEnum.STD_REPO)
        ]

        expected_influencer1 = influencer_dto_generator(num=1)
        expected_influencer1.id = influencers_from_db[0].id
        expected_influencer1.created = influencers_from_db[0].created
        expected_influencer2 = influencer_dto_generator(num=2)
        expected_influencer2.id = influencers_from_db[1].id
        expected_influencer2.created = influencers_from_db[1].created
        expected_influencer3 = influencer_dto_generator(num=3)
        expected_influencer3.id = influencers_from_db[2].id
        expected_influencer3.created = influencers_from_db[2].created
        expected_influencer4 = influencer_dto_generator(num=4)
        expected_influencer4.id = influencers_from_db[3].id
        expected_influencer4.created = influencers_from_db[3].created
        expected_influencers = [
            expected_influencer1,
            expected_influencer2,
            expected_influencer3,
            expected_influencer4
        ]
        self.__influencer_repository.load_collection = MagicMock(return_value=influencers_from_db)
        self.__auth_user_repo.get_by_id = MagicMock(side_effect=[
            user_dto_generator(num=1),
            user_dto_generator(num=2),
            user_dto_generator(num=3),
            user_dto_generator(num=4)
        ])
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_all(PinfluencerContext(response=pinfluencer_response,
                                              event={}))
        assert pinfluencer_response.body == list(map(lambda x: x.__dict__, expected_influencers))
        assert pinfluencer_response.status_code == 200

    def test_create(self):
        influencer_db = create_influencer_dto()
        expected_payload = update_influencer_payload()
        auth_id = "1234"
        event = create_for_auth_user_event(auth_id=auth_id, payload=expected_payload)
        self.__influencer_repository.write_new_for_auth_user = MagicMock(return_value=influencer_db)
        self.__auth_user_repo.update_influencer_claims = MagicMock()
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(response=response,
                                             event=event))
        payload_captor = Captor()
        auth_payload_captor = Captor()
        self.__auth_user_repo.update_influencer_claims.assert_called_once_with(user=auth_payload_captor)
        auth_payload = auth_payload_captor.arg
        assert auth_payload.first_name == expected_payload['first_name']
        assert auth_payload.last_name == expected_payload['last_name']
        assert auth_payload.email == expected_payload['email']
        self.__influencer_repository.write_new_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                                     payload=payload_captor)
        actual_payload: Influencer = payload_captor.arg
        assert valid_uuid(actual_payload.id)
        assert actual_payload.image == TEST_DEFAULT_INFLUENCER_PROFILE_IMAGE
        assert_influencer_creatable_generated_fields_are_equal(expected_payload, actual_payload.__dict__)
        assert response.status_code == 201
        assert response.body == actual_payload.__dict__
        print(response.body)

    def test_create_when_exists(self):
        auth_id = "12341"
        event = create_for_auth_user_event(auth_id=auth_id, payload=update_influencer_payload())
        self.__influencer_repository.write_new_for_auth_user = MagicMock(side_effect=AlreadyExistsException())
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 400
        assert response.body == {}

    def test_create_when_invalid_payload(self):
        auth_id = "12341"
        payload = update_influencer_payload()
        payload['bio'] = 120
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 400
        assert response.body == {}

    def test_update_profile_image(self):
        auth_id = "12341"
        payload = update_image_payload()
        expected_influencer = influencer_dto_generator(num=1)
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__influencer_repository.update_image_for_auth_user = MagicMock(return_value=expected_influencer)
        response = PinfluencerResponse()
        self.__sut.update_profile_image(PinfluencerContext(event=event,
                                                           response=response))
        assert response.status_code == 200
        assert response.body == expected_influencer.__dict__

    def test_update(self):
        influencer_in_db = create_influencer_dto()
        auth_user = update_user_dto()
        self.__auth_user_repo.get_by_id = MagicMock(return_value=auth_user)
        self.__influencer_repository.update_for_auth_user = MagicMock(return_value=influencer_in_db)
        auth_id = "12341"
        response = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(
            event=create_for_auth_user_event(auth_id=auth_id, payload=update_influencer_payload()),
            response=response))
        arg_captor = Captor()
        self.__influencer_repository.update_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                                  payload=arg_captor)
        update_for_auth_user_repo_payload: Influencer = arg_captor.arg
        assert_influencer_update_fields_are_equal(influencer1=update_influencer_payload(),
                                                  influencer2=update_for_auth_user_repo_payload.__dict__)
        assert list(map(lambda x: x.name, update_for_auth_user_repo_payload.values)) == update_influencer_payload()[
            "values"]
        assert list(map(lambda x: x.name, update_for_auth_user_repo_payload.categories)) == update_influencer_payload()[
            "categories"]
        assert response.body == influencer_in_db.__dict__
        assert response.status_code == 200
        assert auth_user.first_name == response.body["first_name"]
        assert auth_user.last_name == response.body["last_name"]
        assert auth_user.email == response.body["email"]
        self.__auth_user_repo.get_by_id.assert_called_once_with(_id=auth_id)

    def test_update_when_not_found(self):
        self.__influencer_repository.update_for_auth_user = MagicMock(
            side_effect=NotFoundException("influencer not found"))
        return_value = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(
            event=create_for_auth_user_event(auth_id="12341", payload=update_influencer_payload()),
            response=return_value))
        assert return_value.body == {}
        assert return_value.status_code == 404

    def test_update_when_payload_not_valid(self):
        payload = update_influencer_payload()
        payload['bio'] = 120
        return_value = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(event=create_for_auth_user_event(auth_id="12341", payload=payload),
                                             response=return_value))
        assert return_value.body == {}
        assert return_value.status_code == 400


class TestBrandController(TestCase):

    def setUp(self):
        self.__brand_repository: BrandRepository = Mock()
        self.__brand_validator = BrandValidator()
        self.__auth_user_repo: AuthUserRepository = Mock()
        self.__sut = BrandController(brand_repository=self.__brand_repository,
                                     brand_validator=self.__brand_validator,
                                     deserializer=JsonCamelToSnakeCaseDeserializer(),
                                     auth_user_repository=self.__auth_user_repo)

    def test_get_by_id(self):
        brand_from_db = brand_dto_generator(num=1, repo=RepoEnum.STD_REPO)
        user_from_auth_db = user_dto_generator(num=1)
        expected_brand = brand_dto_generator(num=1)
        expected_brand.id = brand_from_db.id
        expected_brand.created = brand_from_db.created
        self.__brand_repository.load_by_id = MagicMock(return_value=brand_from_db)
        self.__auth_user_repo.get_by_id = MagicMock(return_value=user_from_auth_db)
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_by_id(PinfluencerContext(event=get_brand_id_event(brand_from_db.id),
                                                response=pinfluencer_response))
        self.__auth_user_repo.get_by_id.assert_called_once_with(_id=brand_from_db.auth_user_id)
        self.__brand_repository.load_by_id.assert_called_once_with(id_=brand_from_db.id)
        assert pinfluencer_response.body == expected_brand.__dict__
        assert pinfluencer_response.is_ok() is True

    def test_get_by_id_when_not_found(self):
        self.__brand_repository.load_by_id = MagicMock(side_effect=NotFoundException())
        field = str(uuid.uuid4())
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_by_id(PinfluencerContext(event=get_brand_id_event(field),
                                                response=pinfluencer_response))
        self.__brand_repository.load_by_id.assert_called_once_with(id_=field)
        assert pinfluencer_response.body == {}
        assert pinfluencer_response.status_code == 404

    def test_get_by_id_when_invalid_uuid(self):
        self.__brand_repository.load_by_id = MagicMock(return_value=None)
        field = "12345"
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_by_id(PinfluencerContext(event=get_brand_id_event(field),
                                                response=pinfluencer_response))
        self.__brand_repository.load_by_id.assert_not_called()
        assert pinfluencer_response.body == {}
        assert pinfluencer_response.status_code == 400

    def test_get_all(self):
        brands_from_db = [
            brand_dto_generator(num=1, repo=RepoEnum.STD_REPO),
            brand_dto_generator(num=2, repo=RepoEnum.STD_REPO),
            brand_dto_generator(num=3, repo=RepoEnum.STD_REPO),
            brand_dto_generator(num=4, repo=RepoEnum.STD_REPO)
        ]

        expected_brand1 = brand_dto_generator(num=1)
        expected_brand1.id = brands_from_db[0].id
        expected_brand1.created = brands_from_db[0].created
        expected_brand2 = brand_dto_generator(num=2)
        expected_brand2.id = brands_from_db[1].id
        expected_brand2.created = brands_from_db[1].created
        expected_brand3 = brand_dto_generator(num=3)
        expected_brand3.id = brands_from_db[2].id
        expected_brand3.created = brands_from_db[2].created
        expected_brand4 = brand_dto_generator(num=4)
        expected_brand4.id = brands_from_db[3].id
        expected_brand4.created = brands_from_db[3].created
        expected_brands = [
            expected_brand1,
            expected_brand2,
            expected_brand3,
            expected_brand4
        ]
        self.__brand_repository.load_collection = MagicMock(return_value=brands_from_db)
        self.__auth_user_repo.get_by_id = MagicMock(side_effect=[
            user_dto_generator(num=1),
            user_dto_generator(num=2),
            user_dto_generator(num=3),
            user_dto_generator(num=4)
        ])
        pinfluencer_response = PinfluencerResponse()
        self.__sut.get_all(PinfluencerContext(event={},
                                              response=pinfluencer_response))
        self.__brand_repository.load_collection.assert_called_once()
        self.__auth_user_repo.get_by_id.assert_has_calls(calls=[
            call(_id=expected_brand1.auth_user_id),
            call(_id=expected_brand2.auth_user_id),
            call(_id=expected_brand3.auth_user_id),
            call(_id=expected_brand4.auth_user_id)
        ], any_order=True)
        assert pinfluencer_response.body == list(map(lambda x: x.__dict__, expected_brands))
        assert pinfluencer_response.status_code == 200

    def test_get(self):
        expected_brand = brand_dto_generator(num=1)
        db_brand = brand_dto_generator(num=1, repo=RepoEnum.STD_REPO)
        expected_brand.id = db_brand.id
        expected_brand.created = db_brand.created
        auth_user = user_dto_generator(num=1)
        self.__brand_repository.load_for_auth_user = MagicMock(return_value=db_brand)
        self.__auth_user_repo.get_by_id = MagicMock(return_value=auth_user)
        auth_id = "12341"
        response = PinfluencerResponse()
        self.__sut.get(PinfluencerContext(event=get_auth_user_event(auth_id),
                                          response=response))
        self.__brand_repository.load_for_auth_user.assert_called_once_with(auth_user_id=auth_id)
        self.__auth_user_repo.get_by_id.assert_called_once_with(_id=auth_id)
        assert response.body == expected_brand.__dict__
        assert response.status_code == 200

    def test_get_when_not_found(self):
        self.__brand_repository.load_for_auth_user = MagicMock(side_effect=NotFoundException())
        auth_id = "12341"
        response = PinfluencerResponse()
        self.__sut.get(PinfluencerContext(event=get_auth_user_event(auth_id),
                                          response=response))
        self.__brand_repository.load_for_auth_user.assert_called_once_with(auth_user_id=auth_id)
        assert response.body == {}
        assert response.status_code == 404

    def test_create(self):
        brand_db = create_brand_dto()
        expected_payload = update_brand_payload()
        auth_id = "12341"
        event = create_for_auth_user_event(auth_id=auth_id, payload=expected_payload)
        self.__brand_repository.write_new_for_auth_user = MagicMock(return_value=brand_db)
        self.__auth_user_repo.update_brand_claims = MagicMock()
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(event=event,
                                             response=response))
        payload_captor = Captor()
        auth_payload_captor = Captor()
        self.__auth_user_repo.update_brand_claims.assert_called_once_with(user=auth_payload_captor)
        auth_payload = auth_payload_captor.arg
        assert auth_payload.first_name == update_brand_payload()['first_name']
        assert auth_payload.last_name == update_brand_payload()['last_name']
        assert auth_payload.email == update_brand_payload()['email']
        self.__brand_repository.write_new_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                                payload=payload_captor)
        actual_payload = payload_captor.arg
        assert valid_uuid(actual_payload.id)
        assert actual_payload.logo == TEST_DEFAULT_BRAND_LOGO
        assert actual_payload.header_image == TEST_DEFAULT_BRAND_HEADER_IMAGE
        assert_brand_creatable_generated_fields_are_equal(expected_payload, actual_payload.__dict__)
        assert response.status_code == 201
        assert response.body == actual_payload.__dict__
        print(response.body)

    def test_create_when_exists(self):
        auth_id = "12341"
        event = create_for_auth_user_event(auth_id=auth_id, payload=update_brand_payload())
        self.__brand_repository.write_new_for_auth_user = MagicMock(side_effect=AlreadyExistsException())
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 400
        assert response.body == {}

    def test_create_when_invalid_payload(self):
        auth_id = "12341"
        payload = update_brand_payload()
        payload['brand_name'] = 120
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        response = PinfluencerResponse()
        self.__sut.create(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 400
        assert response.body == {}

    def test_update(self):
        auth_user = update_user_dto()
        expected_payload = update_brand_payload()
        brand_in_db = update_brand_return_dto()
        expected_dto = update_brand_expected_dto()
        expected_dto.id = brand_in_db.id
        expected_dto.created = brand_in_db.created
        auth_id = "12341"
        event = create_for_auth_user_event(auth_id=auth_id, payload=update_brand_payload())
        self.__brand_repository.update_for_auth_user = MagicMock(return_value=brand_in_db)
        self.__auth_user_repo.get_by_id = MagicMock(return_value=auth_user)
        response = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(event=event,
                                             response=response))
        payload_captor = Captor()
        self.__brand_repository.update_for_auth_user.assert_called_once_with(auth_user_id=auth_id,
                                                                             payload=payload_captor)
        actual_payload = payload_captor.arg
        assert valid_uuid(actual_payload.id)
        assert_brand_updatable_fields_are_equal(actual_payload.__dict__, expected_payload)
        assert list(map(lambda x: x.name, actual_payload.values)) == expected_payload['values']
        assert list(map(lambda x: x.name, actual_payload.categories)) == expected_payload['categories']
        assert response.status_code == 200
        assert response.body == expected_dto.__dict__
        assert response.body["first_name"] == auth_user.first_name
        assert response.body["email"] == auth_user.email
        assert response.body["last_name"] == auth_user.last_name
        self.__auth_user_repo.get_by_id.assert_called_once_with(_id=auth_id)

    def test_update_when_invalid_payload(self):
        auth_id = "12341"
        payload = update_brand_payload()
        payload['brand_name'] = 120
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)

        response = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 400
        assert response.body == {}

    def test_update_when_not_found(self):
        auth_id = "12341"
        payload = update_brand_payload()
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__brand_repository.update_for_auth_user = MagicMock(side_effect=NotFoundException())
        response = PinfluencerResponse()
        self.__sut.update(PinfluencerContext(event=event,
                                             response=response))
        assert response.status_code == 404
        assert response.body == {}

    def test_update_logo(self):
        auth_id = "12341"
        payload = update_image_payload()
        expected_brand = brand_dto_generator(num=1)
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__brand_repository.update_logo_for_auth_user = MagicMock(return_value=expected_brand)
        response = PinfluencerResponse()
        self.__sut.update_logo(PinfluencerContext(event=event,
                                                  response=response))
        assert response.status_code == 200
        assert response.body == expected_brand.__dict__

    def test_update_logo_when_not_found(self):
        auth_id = "12341"
        payload = update_image_payload()
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__brand_repository.update_logo_for_auth_user = MagicMock(side_effect=NotFoundException())
        response = PinfluencerResponse()
        self.__sut.update_logo(PinfluencerContext(event=event,
                                                  response=response))
        assert response.status_code == 404
        assert response.body == {}

    def test_update_header_image(self):
        auth_id = "12341"
        payload = update_image_payload()
        expected_brand = brand_dto_generator(num=1)
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__brand_repository.update_header_image_for_auth_user = MagicMock(return_value=expected_brand)
        response = PinfluencerResponse()
        self.__sut.update_header_image(PinfluencerContext(event=event,
                                                          response=response))
        assert response.status_code == 200
        assert response.body == expected_brand.__dict__

    def test_update_header_image_when_not_found(self):
        auth_id = "12341"
        payload = update_image_payload()
        event = create_for_auth_user_event(auth_id=auth_id, payload=payload)
        self.__brand_repository.update_header_image_for_auth_user = MagicMock(side_effect=NotFoundException())
        response = PinfluencerResponse()
        self.__sut.update_header_image(PinfluencerContext(event=event,
                                                          response=response))
        assert response.status_code == 404
        assert response.body == {}
