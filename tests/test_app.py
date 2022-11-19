from os.path import exists
from typing import Union
from unittest import TestCase
from unittest.mock import Mock, MagicMock

from callee import Any
from cfn_tools import load_yaml
from simple_injection import ServiceCollection

from src.app import bootstrap
from src.web import PinfluencerContext, PinfluencerResponse
from src.web.middleware import MiddlewarePipeline
from src.web.routing import Dispatcher
from src.web.sequences import NotImplementedSequenceBuilder, UpdateImageForListingSequenceBuilder, \
    UpdateListingSequenceBuilder, CreateListingSequenceBuilder, GetListingByIdSequenceBuilder, \
    GetListingsForBrandSequenceBuilder, UpdateInfluencerImageSequenceBuilder, UpdateInfluencerSequenceBuilder, \
    CreateInfluencerSequenceBuilder, GetAuthInfluencerSequenceBuilder, GetInfluencerByIdSequenceBuilder, \
    GetAllInfluencersSequenceBuilder, UpdateBrandImageSequenceBuilder, UpdateBrandSequenceBuilder, \
    CreateBrandSequenceBuilder, GetAuthBrandSequenceBuilder, GetBrandByIdSequenceBuilder, GetAllBrandsSequenceBuilder, \
    CreateNotificationSequenceBuilder, GetNotificationByIdSequenceBuilder, CreateAudienceAgeSequenceBuilder, \
    GetAudienceAgeSequenceBuilder, UpdateAudienceAgeSequenceBuilder, CreateAudienceGenderSequenceBuilder, \
    GetAudienceGenderSequenceBuilder, UpdateAudienceGenderSequenceBuilder
from tests import get_as_json


class TestRoutes(TestCase):

    def setUp(self) -> None:
        self.__ioc: ServiceCollection = ServiceCollection()
        self.__mock_middleware_pipeline: MiddlewarePipeline = Mock()

    def test_server_error(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock(side_effect=Exception("some exception"))

        # act
        response = bootstrap(event={"routeKey": "GET /brands/{brand_id}"},
                             context={},
                             middleware=self.__mock_middleware_pipeline,
                             ioc=self.__ioc,
                             data_manager=Mock(),
                             cognito_auth_service=Mock())

        # assert
        assert response == get_as_json(status_code=500,
                                       body="""{"message": "unexpected server error, please try later :("}""")

    def test_route_that_does_not_exist(self):
        self.__assert_non_service_layer_route(route_key="GET /random",
                                              expected_body="""{"message": "route: GET /random not found"}""",
                                              expected_status_code=404)

    def test_feed(self):
        self.__assert_not_implemented(route="GET /feed")

    def test_get_all_brands(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /brands"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAllBrandsSequenceBuilder))

    def test_get_brand_by_id(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /brands/{brand_id}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetBrandByIdSequenceBuilder))

    def test_get_all_influencers(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /influencers"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAllInfluencersSequenceBuilder))

    def test_get_influencer_by_id(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /influencers/{influencer_id}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetInfluencerByIdSequenceBuilder))

    def test_get_auth_brand(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /brands/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAuthBrandSequenceBuilder))

    def test_create_auth_brand(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /brands/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateBrandSequenceBuilder))

    def test_update_auth_brand(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "PATCH /brands/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateBrandSequenceBuilder))

    def test_create_or_replace_auth_brand_image(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /brands/me/images/{image_field}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateBrandImageSequenceBuilder))

    def test_get_auth_influencer(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /influencers/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAuthInfluencerSequenceBuilder))

    def test_create_auth_influencer(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /influencers/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateInfluencerSequenceBuilder))

    def test_update_auth_influencer_image(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /influencers/me/images/{image_field}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateInfluencerImageSequenceBuilder))

    def test_update_auth_influencer(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "PATCH /influencers/me"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateInfluencerSequenceBuilder))

    def test_create_auth_brand_listing(self):  # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /brands/me/listings"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateListingSequenceBuilder))

    def test_get_listing_by_id(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /listings/{listing_id}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetListingByIdSequenceBuilder))

    def test_get_auth_brand_listings(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /brands/me/listings"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetListingsForBrandSequenceBuilder))

    def test_update_brand_auth_listing_by_id(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "PATCH /brands/me/listings/{listing_id}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateListingSequenceBuilder))

    def test_delete_brand_auth_listing_by_id(self):
        self.__assert_not_implemented(route="DELETE /brands/me/listings/{listing_id}")

    def test_create_listing_product_image(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /brands/me/listings/{listing_id}/images/{image_field}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateImageForListingSequenceBuilder))

    def test_get_notification_by_id(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /notifications/{notification_id}"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetNotificationByIdSequenceBuilder))

    def test_get_collaboration_by_id(self):
        self.__assert_not_implemented(route="GET /collaborations/{collaboration_id}")

    def test_create_collaboration(self):
        self.__assert_not_implemented(route="POST /influencers/me/collaborations")

    def test_update_collaboration(self):
        self.__assert_not_implemented(route="PATCH /influencers/me/collaborations/{collaboration_id}")

    def test_get_collaborations_for_brand(self):
        self.__assert_not_implemented(route="GET /brands/me/collaborations")

    def test_get_collaborations_for_influencer(self):
        self.__assert_not_implemented(route="GET /influencers/me/collaborations")

    def test_get_notifications_for_sender(self):
        self.__assert_not_implemented(route="GET /senders/me/notifications")

    def test_get_notifications_for_receiver(self):
        self.__assert_not_implemented(route="GET /receivers/me/notifications")

    def test_create_notification_for_user(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /users/me/notifications"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateNotificationSequenceBuilder))

    def test_update_notification_for_user(self):
        self.__assert_not_implemented(route="PATCH /users/me/notifications")

    def test_get_audience_age_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /influencers/me/audience-age-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAudienceAgeSequenceBuilder))

    def test_get_audience_gender_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "GET /influencers/me/audience-gender-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(GetAudienceGenderSequenceBuilder))

    def test_create_audience_age_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /influencers/me/audience-age-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateAudienceAgeSequenceBuilder))

    def test_create_audience_gender_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "POST /influencers/me/audience-gender-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(CreateAudienceGenderSequenceBuilder))

    def test_update_audience_age_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "PATCH /influencers/me/audience-age-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateAudienceAgeSequenceBuilder))

    def test_update_audience_gender_splits(self):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()

        # act
        bootstrap(event={"routeKey": "PATCH /influencers/me/audience-gender-splits"},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        self.__mock_middleware_pipeline \
            .execute_middleware \
            .assert_called_once_with(context=Any(),
                                     sequence=self.__ioc.resolve(UpdateAudienceGenderSequenceBuilder))

    def test_template_matches_routes(self):
        template_file_path = f"./../template.yaml"
        if not exists(template_file_path):
            template_file_path = f"./template.yaml"
        with open(template_file_path) as file:
            yaml_str = file.read()
            data = load_yaml(yaml_str)
            paths = sorted([f"{event[1]['Properties']['Method'].upper()} {event[1]['Properties']['Path']}" for event in
                            data["Resources"]["PinfluencerFunction"]["Properties"]["Events"].items()])
            route_paths = sorted([*Dispatcher(service_locator=Mock()).dispatch_route_to_ctr])
            assert paths == route_paths

    def __assert_service_endpoint_200(self,
                                      expected_body: str,
                                      actual_body: Union[dict, list],
                                      route_key: str,
                                      service_function: str,
                                      service_name: str):
        # arrange
        service = Mock()
        setattr(service, service_function,
                MagicMock(side_effect=lambda x: self.__service_side_effect(context=x, actual_body=actual_body)))
        setattr(self.__ioc, service_name, MagicMock(return_value=service))

        # act
        response = bootstrap(event={"routeKey": route_key},
                             context={},
                             middleware=self.__mock_middleware_pipeline,
                             ioc=self.__ioc,
                             data_manager=Mock(),
                             cognito_auth_service=Mock())

        # assert
        assert response == get_as_json(status_code=200, body=expected_body)

    def __service_side_effect(self, context: PinfluencerContext, actual_body: dict):
        context.response.body = actual_body

    def __assert_non_service_layer_route(self,
                                         route_key: str,
                                         expected_body: str,
                                         expected_status_code: int):
        """
        any routes that do not access services from IOC container, like not found or not implemented routes
        """

        # arrange/act
        response = bootstrap(event={"routeKey": route_key},
                             context={},
                             middleware=self.__mock_middleware_pipeline,
                             ioc=self.__ioc,
                             data_manager=Mock(),
                             cognito_auth_service=Mock())

        # assert
        assert response == get_as_json(status_code=expected_status_code, body=expected_body)

    def __assert_not_implemented(self, route: str):
        # arrange
        self.__mock_middleware_pipeline.execute_middleware = MagicMock()
        context = PinfluencerContext(response=PinfluencerResponse())

        # act
        bootstrap(event={"routeKey": route},
                  context={},
                  middleware=self.__mock_middleware_pipeline,
                  ioc=self.__ioc,
                  data_manager=Mock(),
                  cognito_auth_service=Mock())

        # assert
        with self.subTest(msg="pipeline executes once"):
            self.__mock_middleware_pipeline \
                .execute_middleware \
                .assert_called_once_with(context=Any(),
                                         sequence=self.__ioc.resolve(NotImplementedSequenceBuilder))
