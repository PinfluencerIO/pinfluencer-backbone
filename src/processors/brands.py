from src.data_access_layer import to_list
from src.data_access_layer.brand import Brand
from src.data_access_layer.read_data_access import load_all_products_for_brand_id
from src.data_access_layer.write_data_access import write_new_brand, update_brand
from src.filters import FilterInterface
from src.filters.authorised_filter import GetBrandAssociatedWithCognitoUser, NoBrandAssociatedWithCognitoUser
from src.filters.payload_validation import BrandPostPayloadValidation, BrandPutPayloadValidation
from src.filters.valid_id_filters import LoadResourceById
from src.interfaces.data_manager_interface import DataManagerInterface
from src.pinfluencer_response import PinfluencerResponse
from src.processors import ProcessInterface, get_user


class ProcessPublicBrands(ProcessInterface):
    def __init__(self, data_manager: DataManagerInterface):
        super().__init__(data_manager)

    def do_process(self, event: dict) -> PinfluencerResponse:
        return PinfluencerResponse(body=to_list(self._data_manager.session
                                                .query(Brand)
                                                .all()))


class ProcessPublicGetBrandBy:
    def __init__(self, load_resource_by_id: LoadResourceById):
        self.load_resource_by_id = load_resource_by_id

    def do_process(self, event: dict) -> PinfluencerResponse:
        response = self.load_resource_by_id.load(event)
        if response.is_success():
            return PinfluencerResponse(body=response.get_payload())
        else:
            return PinfluencerResponse.as_400_error(response.get_message())


class ProcessPublicAllProductsForBrand:
    def __init__(self, load_resource_by_id: LoadResourceById, data_manager: DataManagerInterface):
        self.load_resource_by_id = load_resource_by_id
        self.data_manager = data_manager

    def do_process(self, event: dict) -> PinfluencerResponse:
        response = self.load_resource_by_id.load(event)
        if response.is_success():
            brand = response.get_payload()
            products_for_brand = load_all_products_for_brand_id(brand['id'], self.data_manager)
            return PinfluencerResponse(body=(to_list(products_for_brand)))
        else:
            return PinfluencerResponse.as_400_error(response.get_message())


class ProcessAuthenticatedGetBrand:
    def __init__(self, auth_filter: GetBrandAssociatedWithCognitoUser, data_manager: DataManagerInterface):
        self.auth_filter = auth_filter
        self.data_manager = data_manager

    def do_process(self, event: dict) -> PinfluencerResponse:
        filter_response = self.get_authenticated_brand(event)

        if filter_response.is_success():
            return PinfluencerResponse(filter_response.get_code(), filter_response.get_payload())
        else:
            return PinfluencerResponse(404, "No brand associated with auth_key")

    def get_authenticated_brand(self, event):
        return self.auth_filter.do_filter(event)


class ProcessAuthenticatedPutBrand:
    def __init__(self,
                 get_brand_associated_with_cognito_user: GetBrandAssociatedWithCognitoUser,
                 put_validation: BrandPutPayloadValidation,
                 data_manager: DataManagerInterface):
        self.get_brand_associated_with_cognito_user = get_brand_associated_with_cognito_user
        self.put_validation = put_validation
        self.data_manager = data_manager

    def do_process(self, event: dict) -> PinfluencerResponse:
        filter_response = self.call_get_brand_associated_with_cognito_user(event)
        if filter_response.is_success():

            brand = filter_response.get_payload()
            filter_response = self.validate_update_brand_payload(event)
            if filter_response.is_success():
                update_email(filter_response.get_payload(), event)
                id_ = brand['id']
                payload = filter_response.get_payload()
                updated_brand = self.update_brand(id_, payload)
                return PinfluencerResponse(200, updated_brand.as_dict())
            else:
                return PinfluencerResponse(filter_response.get_code(), filter_response.get_message())
        else:
            return PinfluencerResponse(401, filter_response.get_message())

    def update_brand(self, brand_id, payload) -> Brand:
        return update_brand(brand_id, payload, self.data_manager)

    def validate_update_brand_payload(self, event):
        return self.put_validation.do_filter(event)

    def call_get_brand_associated_with_cognito_user(self, event):
        return self.get_brand_associated_with_cognito_user.do_filter(event)


class ProcessAuthenticatedPostBrand:
    def __init__(self, no_associated_brand_with_cognito_user: NoBrandAssociatedWithCognitoUser,
                 post_validation: BrandPostPayloadValidation,
                 data_manager: DataManagerInterface):
        self.post_validation = post_validation
        self.no_associated_brand_with_cognito_user = no_associated_brand_with_cognito_user
        self.data_manager = data_manager

    def do_process(self, event: dict) -> PinfluencerResponse:
        filter_response = self.check_no_brand_associated_with_authenticated_user(event)
        if filter_response.is_success():
            filter_response = self.validate_new_brand_payload(event)
            if filter_response.is_success():
                payload = filter_response.get_payload()
                payload["auth_user_id"] = get_user(event=event)
                update_email(payload, event)
                image_bytes = payload['image']
                payload['image'] = None
                brand = self.create_new_brand(payload, image_bytes)
                return PinfluencerResponse(201, brand.as_dict())
            else:
                return PinfluencerResponse(filter_response.get_code())
        else:
            return PinfluencerResponse(filter_response.get_code())

    def create_new_brand(self, payload, image_bytes) -> Brand:
        return write_new_brand(payload, image_bytes, self.data_manager)

    def validate_new_brand_payload(self, event):
        return self.post_validation.do_filter(event)

    def check_no_brand_associated_with_authenticated_user(self, event):
        return self.no_associated_brand_with_cognito_user.do_filter(event)


class ProcessAuthenticatedPatchBrandImage:
    def __init__(self,
                 auth_filter: FilterInterface,
                 brand_image_patch_payload_validation: FilterInterface,
                 update_brand_image,
                 data_manager: DataManagerInterface) -> None:
        self.auth_filter = auth_filter
        self.brand_image_patch_payload_validation = brand_image_patch_payload_validation
        self.update_brand_image = update_brand_image
        self.data_manager = data_manager

    def do_process(self, event: dict) -> PinfluencerResponse:
        filter_response = self.auth_filter.do_filter(event)
        if filter_response.is_success():
            brand = filter_response.get_payload()
            filter_response = self.brand_image_patch_payload_validation.do_filter(event)
            if filter_response.is_success():
                filter_response = self.brand_image_patch_payload_validation.do_filter(event)
                if filter_response.is_success():
                    updated_brand = self.update_brand_image(brand['id'],
                                                            filter_response.get_payload()['image'],
                                                            self.data_manager)
                    return PinfluencerResponse(200, updated_brand.as_dict())
                else:
                    return PinfluencerResponse(filter_response.get_code(), filter_response.get_message())
            else:
                return PinfluencerResponse(filter_response.get_code(), filter_response.get_message())
        else:
            return PinfluencerResponse(filter_response.get_code(), filter_response.get_message())


def update_email(body, event):
    if ('email' in event['requestContext']['authorizer']['jwt']['claims'] and
            event['requestContext']['authorizer']['jwt']['claims']['email'] is not None):
        print(f"Found email in claim: {event['requestContext']['authorizer']['jwt']['claims']['email']}")
        print(f'before {body}')
        body['email'] = event['requestContext']['authorizer']['jwt']['claims']['email']
        print(f'after {body}')
