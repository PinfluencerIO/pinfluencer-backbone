from jsonschema.exceptions import ValidationError

from src.crosscutting import print_exception
from src.domain.models import Brand, Influencer
from src.domain.validation import BrandValidator, InfluencerValidator, CampaignValidator
from src.types import AuthUserRepository, Deserializer
from src.web import PinfluencerContext
from src.web.validation import valid_path_resource_id

S3_URL = "https://pinfluencer-product-images.s3.eu-west-2.amazonaws.com/"


class CommonBeforeHooks:

    def __init__(self, deserializer: Deserializer):
        self.__deserializer = deserializer

    def set_body(self, context: PinfluencerContext):
        context.body = self.__deserializer.deserialize(data=context.event["body"])


class CampaignBeforeHooks:

    def __init__(self, campaign_validator: CampaignValidator):
        self.__campaign_validator = campaign_validator

    def validate_campaign(self, context: PinfluencerContext):
        try:
            self.__campaign_validator.validate_campaign(payload=context.body)
        except ValidationError as e:
            print_exception(e)
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400


class CampaignAfterHooks:

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        context.response.body["product_image1"] = f"{S3_URL}/{context.response.body['product_image1']}"
        context.response.body["product_image2"] = f"{S3_URL}/{context.response.body['product_image2']}"
        context.response.body["product_image3"] = f"{S3_URL}/{context.response.body['product_image3']}"


class InfluencerBeforeHooks:

    def __init__(self, influencer_validator: InfluencerValidator):
        self.__influencer_validator = influencer_validator


    def validate_uuid(self, context: PinfluencerContext):
        id = valid_path_resource_id(event=context.event, resource_key="influencer_id")
        if not id:
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400
        else:
            context.id = id

    def validate_influencer(self, context: PinfluencerContext):
        try:
            self.__influencer_validator.validate_influencer(payload=context.body)
        except ValidationError as e:
            print_exception(e)
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400


class BrandBeforeHooks:

    def __init__(self, brand_validator: BrandValidator):
        self.__brand_validator = brand_validator

    def validate_uuid(self, context: PinfluencerContext):
        id = valid_path_resource_id(event=context.event, resource_key="brand_id")
        if not id:
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400
        else:
            context.id = id

    def validate_brand(self, context: PinfluencerContext):
        try:
            self.__brand_validator.validate_brand(payload=context.body)
        except ValidationError as e:
            print_exception(e)
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400


class BrandAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository):
        self.__auth_user_repository = auth_user_repository

    def set_brand_claims(self, context: PinfluencerContext):
        user = Brand(first_name=context.body["first_name"],
                     last_name=context.body["last_name"],
                     email=context.body["email"],
                     auth_user_id=context.auth_user_id)
        self.__auth_user_repository.update_brand_claims(user=user)

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        context.response.body["header_image"] = f"{S3_URL}/{context.response.body['header_image']}"
        context.response.body["logo"] = f"{S3_URL}/{context.response.body['logo']}"

    def tag_bucket_url_to_images_collection(self, context: PinfluencerContext):
        for brand in context.response.body:
            brand["header_image"] = f"{S3_URL}/{brand['header_image']}"
            brand["logo"] = f"{S3_URL}/{brand['logo']}"


class InfluencerAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository):
        self.__auth_user_repository = auth_user_repository

    def set_influencer_claims(self, context: PinfluencerContext):
        user = Influencer(first_name=context.body["first_name"],
                     last_name=context.body["last_name"],
                     email=context.body["email"],
                     auth_user_id=context.auth_user_id)
        self.__auth_user_repository.update_influencer_claims(user=user)

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        context.response.body["image"] = f"{S3_URL}/{context.response.body['image']}"

    def tag_bucket_url_to_images_collection(self, context: PinfluencerContext):
        for influencer in context.response.body:
            influencer["image"] = f"{S3_URL}/{influencer['image']}"


class UserBeforeHooks:

    def set_auth_user_id(self, context: PinfluencerContext):
        context.auth_user_id = context.event['requestContext']['authorizer']['jwt']['claims']['username']


class UserAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository):
        self.__auth_user_repository = auth_user_repository

    def tag_auth_user_claims_to_response(self, context: PinfluencerContext):
        auth_user = self.__auth_user_repository.get_by_id(_id=context.response.body["auth_user_id"])
        context.response.body["first_name"] = auth_user.first_name
        context.response.body["last_name"] = auth_user.last_name
        context.response.body["email"] = auth_user.email

    def tag_auth_user_claims_to_response_collection(self, context: PinfluencerContext):
        for user in context.response.body:
            auth_user = self.__auth_user_repository.get_by_id(_id=user["auth_user_id"])
            user["first_name"] = auth_user.first_name
            user["last_name"] = auth_user.last_name
            user["email"] = auth_user.email


class HooksFacade:

    def __init__(self, common_hooks: CommonBeforeHooks,
                 brand_after_hooks: BrandAfterHooks,
                 influencer_after_hooks: InfluencerAfterHooks,
                 user_before_hooks: UserBeforeHooks,
                 user_after_hooks: UserAfterHooks,
                 influencer_before_hooks: InfluencerBeforeHooks,
                 brand_before_hooks: BrandBeforeHooks,
                 campaign_before_hooks: CampaignBeforeHooks):
        self.__campaign_before_hooks = campaign_before_hooks
        self.__brand_before_hooks = brand_before_hooks
        self.__influencer_before_hooks = influencer_before_hooks
        self.__user_after_hooks = user_after_hooks
        self.__influencer_after_hooks = influencer_after_hooks
        self.__user_before_hooks = user_before_hooks
        self.__brand_after_hooks = brand_after_hooks
        self.__common_before_hooks = common_hooks

    def get_campaign_before_hooks(self) -> CampaignBeforeHooks:
        return self.__campaign_before_hooks

    def get_brand_before_hooks(self) -> BrandBeforeHooks:
        return self.__brand_before_hooks

    def get_influencer_before_hooks(self) -> InfluencerBeforeHooks:
        return self.__influencer_before_hooks

    def get_user_after_hooks(self) -> UserAfterHooks:
        return self.__user_after_hooks

    def get_influencer_after_hooks(self) -> InfluencerAfterHooks:
        return self.__influencer_after_hooks

    def get_user_before_hooks(self) -> UserBeforeHooks:
        return self.__user_before_hooks

    def get_brand_after_hooks(self) -> BrandAfterHooks:
        return self.__brand_after_hooks

    def get_before_common_hooks(self) -> CommonBeforeHooks:
        return self.__common_before_hooks
