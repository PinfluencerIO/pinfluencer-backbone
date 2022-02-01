from collections import OrderedDict

from src.data_access_layer.read_data_access import load_collection
from src.data_access_layer.write_data_access import db_write_new_brand_for_auth_user, \
    db_write_update_brand_for_auth_user, db_write_patch_brand_image_for_auth_user
from src.pinfluencer_response import PinfluencerResponse
from src.processors import valid_uuid, types, get_cognito_user
from src.processors.get_collection import ProcessGetCollection
from src.processors.ok_response import ProcessOkResponse
from src.processors.write_for_auth_user import ProcessWriteForAuthenticatedUser


class Controller:
    def __init__(self, data_manager) -> None:
        self._data_manager = data_manager


class FeedController(Controller):
    def __init__(self, data_manager) -> None:
        super().__init__(data_manager)

    def handle_feed(self, event):
        return ProcessOkResponse().do_process(event)


class BrandController(Controller):
    def __init__(self, data_manager, image_repo, brand_repository) -> None:
        super().__init__(data_manager)
        self.__type_ = 'brand'
        self.__brand_repository = brand_repository
        self._image_repository = image_repo

    def handle_get_all_brands(self, event):
        return PinfluencerResponse(status_code=200, body=list(map(lambda x: x.__dict__, self.__brand_repository.load_collection())))

    def handle_get_by_id(self, event):
        id_ = valid_path_resource_id(event, types[self.__type_]['key'])
        if id_:
            brand = self.__brand_repository.load_by_id(id_=id_)
            if brand:
                return PinfluencerResponse(status_code=200, body=brand.__dict__)
        return PinfluencerResponse(status_code=404, body={})

    def handle_get_brand(self, event):
        auth_user_id = get_cognito_user(event)
        return PinfluencerResponse(status_code=200, body=self.__brand_repository.load_for_auth_user(auth_user_id=auth_user_id).__dict__)

    def handle_create_brand(self, event):
        return ProcessWriteForAuthenticatedUser('brand', 'post', db_write_new_brand_for_auth_user,
                                                self._data_manager,
                                                self._image_repository).do_process(event)

    def handle_update_brand(self, event):
        return ProcessWriteForAuthenticatedUser('brand', 'put', db_write_update_brand_for_auth_user,
                                                self._data_manager,
                                                self._image_repository).do_process(event)

    def handle_update_brand_image(self, event):
        return ProcessWriteForAuthenticatedUser('brand', 'patch',
                                                db_write_patch_brand_image_for_auth_user,
                                                self._data_manager,
                                                self._image_repository).do_process(event)


class InfluencerController(Controller):
    def __init__(self, data_manager, image_repo) -> None:
        super().__init__(data_manager)
        self._image_repository = image_repo

    def handle_get_all_influencers(self, event):
        return ProcessGetCollection('influencers', load_collection, self._data_manager).do_process(event)

    def handle_get_by_id(self, event):
        return None

    def handle_get_influencer(self, event):
        raise NotImplemented

    def handle_create_influencer(self, event):
        raise NotImplemented

    def handle_update_influencer(self, event):
        raise NotImplemented

    def handle_update_influencer_image(self, event):
        raise NotImplemented


class CampaignController(Controller):
    def __init__(self, data_manager, image_repo) -> None:
        super().__init__(data_manager)
        self._image_repository = image_repo

    def handle_get_all_campaigns(self, event):
        raise NotImplemented


class Routes:
    def __init__(self, data_manager, image_repository):
        self.__feed_ctr = FeedController(data_manager)
        self.__brand_ctr = BrandController(data_manager, image_repository, brand_repository=None)
        self.__influencer_ctr = InfluencerController(data_manager, image_repository)
        self.__campaign_ctr = CampaignController(data_manager, image_repository)

    @property
    def routes(self):

        feed = OrderedDict(
            {'GET /feed': self.__feed_ctr.handle_feed}
        )

        users = OrderedDict(
            {
                'GET /brands': self.__brand_ctr.handle_get_all_brands,

                'GET /influencers': self.__influencer_ctr.handle_get_all_influencers,

                'GET /brands/{brand_id}': self.__brand_ctr.handle_get_by_id,

                'GET /influencers/{influencer_id}': self.__influencer_ctr.handle_get_by_id,

                # authenticated brand endpoints
                'GET /brands/me': self.__brand_ctr.handle_get_brand,

                'POST /brands/me': self.__brand_ctr.handle_create_brand,

                'PUT /brands/me': self.__brand_ctr.handle_update_brand,

                'PATCH /brands/me/image': self.__brand_ctr.handle_update_brand_image,

                # authenticated influencer endpoints
                'GET /influencers/me': self.__influencer_ctr.handle_get_influencer,

                'POST /influencers/me': self.__influencer_ctr.handle_create_influencer,

                'PUT /influencers/me': self.__influencer_ctr.handle_update_influencer,

                'PATCH /influencers/me/image': self.__influencer_ctr.handle_update_influencer_image,
            }
        )

        campaigns = OrderedDict(
            {'GET /campaigns/me': self.__campaign_ctr.handle_get_all_campaigns}
        )

        routes = {}
        routes.update(feed)
        routes.update(users)
        routes.update(campaigns)
        return routes


def valid_path_resource_id(event, resource_key):
    try:
        id_ = event['pathParameters'][resource_key]
        if valid_uuid(id_):
            return id_
        else:
            print(f'Path parameter not a valid uuid {id_}')
    except KeyError:
        print(f'Missing key in event pathParameters.{resource_key}')

    return None