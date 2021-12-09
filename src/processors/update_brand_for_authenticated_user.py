from src.data_access_layer.brand import Brand
from src.data_access_layer.write_data_access import update_brand
from src.filters.authorised_filter import GetBrandAssociatedWithCognitoUser
from src.filters.payload_validation import BrandPutPayloadValidation
from src.interfaces.data_manager_interface import DataManagerInterface
from src.pinfluencer_response import PinfluencerResponse
from src.processors import protect_email_from_update_if_held_in_claims


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
                protect_email_from_update_if_held_in_claims(filter_response.get_payload(), event)
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