from src.web import PinfluencerResponse, get_cognito_user, BRAND_ID_PATH_KEY
from src.web.validation import valid_path_resource_id


class BrandController:
    def __init__(self, brand_repository):
        self.__brand_repository = brand_repository

    def get_all(self, event):
        return PinfluencerResponse(status_code=200, body=list(map(lambda x: x.__dict__,
                                                                  self.__brand_repository.load_collection())))

    def get_by_id(self, event):
        id_ = valid_path_resource_id(event, BRAND_ID_PATH_KEY)
        if id_:
            brand = self.__brand_repository.load_by_id(id_=id_)
            if brand:
                return PinfluencerResponse(status_code=200, body=brand.__dict__)
            return PinfluencerResponse(status_code=404, body={})
        return PinfluencerResponse(status_code=400, body={})

    def get(self, event):
        auth_user_id = get_cognito_user(event)
        if auth_user_id:
            brand = self.__brand_repository.load_for_auth_user(auth_user_id=auth_user_id)
            if brand:
                return PinfluencerResponse(status_code=200, body=brand.__dict__)
        return PinfluencerResponse(status_code=404, body={})

    def create(self, event):
        raise NotImplemented

    def update(self, event):
        raise NotImplemented

    def update_header_image(self, event):
        raise NotImplemented

    def update_logo(self, event):
        raise NotImplemented
