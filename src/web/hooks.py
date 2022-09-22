from jsonschema.exceptions import ValidationError

from src._types import AuthUserRepository, Deserializer, BrandRepository, ImageRepository
from src.crosscutting import print_exception, PinfluencerObjectMapper
from src.domain.models import CategoryEnum, ValueEnum, CampaignStateEnum, User
from src.domain.validation import BrandValidator, InfluencerValidator, CampaignValidator
from src.exceptions import NotFoundException
from src.web import PinfluencerContext, valid_path_resource_id
from src.web.views import RawImageRequestDto, ImageRequestDto

S3_URL = "https://pinfluencer-product-images.s3.eu-west-2.amazonaws.com"


class CommonAfterHooks:

    def map_enum(self,
                 context: PinfluencerContext,
                 key: str):
        self.__map_enum_base(entity=context.response.body,
                             key=key)

    def map_enum_collection(self,
                            context: PinfluencerContext,
                            key: str):
        for entity in context.response.body:
            self.__map_enum_base(entity=entity,
                                 key=key)

    def map_enums(self,
                  context: PinfluencerContext,
                  key: str):
        self.__map_enums_base(entity=context.response.body,
                              key=key)

    def __map_enum_base(self, entity: dict,
                        key: str):
        entity[key] = entity[key].name

    def __map_enums_base(self, entity: dict,
                         key: str):
        entity[key] = list(map(lambda x: x.name, entity[key]))

    def map_enums_collection(self,
                             context: PinfluencerContext,
                             key: str):
        for entity in context.response.body:
            self.__map_enums_base(entity=entity, key=key)

    def set_image_url(self,
                      context: PinfluencerContext,
                      image_fields: list[str],
                      collection: bool = False):
        if collection:
            for entity in context.response.body:
                self.__set_image_fields(entity=entity, fields=image_fields)
        else:
            self.__set_image_fields(entity=context.response.body, fields=image_fields)

    def __set_image_fields(self, entity: dict, fields: list[str]):
        for field in fields:
            self.__set_image(entity=entity, field=field)

    def __set_image(self, entity: dict, field: str):
        if entity[field] is not None:
            entity[field] = f'{S3_URL}/{entity[field]}'


class CommonBeforeHooks:

    def __init__(self, deserializer: Deserializer,
                 image_repo: ImageRepository,
                 object_mapper: PinfluencerObjectMapper):
        self.__object_mapper = object_mapper
        self.__image_repo = image_repo
        self.__deserializer = deserializer

    def validate_image_path(self, context: PinfluencerContext,
                            possible_paths: list[str]):
        if not possible_paths.__contains__(context.event['pathParameters']["image_field"]):
            context.response.status_code = 400
            context.response.body = {}
            context.short_circuit = True
            print(f"{context.event['pathParameters']['image_field']} is not a valid image field")


    def upload_image(self, context: PinfluencerContext,
                     path: str,
                     map_list: dict):
        request: RawImageRequestDto = self.__object_mapper.map_from_dict(_from=context.body, to=RawImageRequestDto)
        key = self.__image_repo.upload(path=path, image_base64_encoded=request.image_bytes)
        context.body = ImageRequestDto(image_path=key, image_field=map_list[context.event['pathParameters']['image_field']]).__dict__

    def map_enum(self, context: PinfluencerContext,
                 key: str,
                 enum_value):
        context.body[key] = enum_value[context.body[key]]

    def map_enums(self, context: PinfluencerContext,
                  key: str,
                  enum_value):
        context.body[key] = list(map(lambda x: enum_value[x], context.body[key]))

    def set_body(self, context: PinfluencerContext):
        context.body = self.__deserializer.deserialize(data=context.event["body"])


class CampaignBeforeHooks:

    def __init__(self, campaign_validator: CampaignValidator,
                 common_before_hooks: CommonBeforeHooks):
        self.__common_before_hooks = common_before_hooks
        self.__campaign_validator = campaign_validator

    def map_campaign_categories_and_values(self, context: PinfluencerContext):
        self.__common_before_hooks.map_enums(context=context,
                                             key="campaign_categories",
                                             enum_value=CategoryEnum)
        self.__common_before_hooks.map_enums(context=context,
                                             key="campaign_values",
                                             enum_value=ValueEnum)

    def map_campaign_state(self, context: PinfluencerContext):
        self.__common_before_hooks.map_enum(context=context,
                                            key="campaign_state",
                                            enum_value=CampaignStateEnum)

    def validate_campaign(self, context: PinfluencerContext):
        try:
            self.__campaign_validator.validate_campaign(payload=context.body)
        except ValidationError as e:
            print_exception(e)
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400

    def validate_id(self, context: PinfluencerContext):
        id = valid_path_resource_id(event=context.event, resource_key="campaign_id")
        if not id:
            context.short_circuit = True
            context.response.body = {}
            context.response.status_code = 400
        else:
            context.id = id

    def upload_image(self, context: PinfluencerContext):
        self.__common_before_hooks.upload_image(path=f"campaigns/{context.auth_user_id}", context=context, map_list={
            "product-image": "product_image"
        })

    def validate_image_key(self, context: PinfluencerContext):
        self.__common_before_hooks.validate_image_path(context=context, possible_paths=["product_image"])


class CampaignAfterHooks:

    def __init__(self, common_after_hooks: CommonAfterHooks):
        self.__common_after_hooks = common_after_hooks

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        self.__common_after_hooks.set_image_url(context=context,
                                                image_fields=["product_image1",
                                                              "product_image2",
                                                              "product_image3"],
                                                collection=False)

    def format_values_and_categories(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enums(context=context,
                                            key="campaign_values")
        self.__common_after_hooks.map_enums(context=context,
                                            key="campaign_categories")

    def tag_bucket_url_to_images_collection(self, context: PinfluencerContext):
        self.__common_after_hooks.set_image_url(context=context,
                                                image_fields=["product_image1",
                                                              "product_image2",
                                                              "product_image3"],
                                                collection=True)

    def format_values_and_categories_collection(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enums_collection(context=context,
                                                       key="campaign_values")
        self.__common_after_hooks.map_enums_collection(context=context,
                                                       key="campaign_categories")

    def format_campaign_state_collection(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enum_collection(context=context,
                                                      key="campaign_state")

    def format_campaign_state(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enum(context=context,
                                           key="campaign_state")


class InfluencerBeforeHooks:

    def __init__(self, influencer_validator: InfluencerValidator,
                 common_before_hooks: CommonBeforeHooks):
        self.__common_before_hooks = common_before_hooks
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

    def upload_image(self, context: PinfluencerContext):
        self.__common_before_hooks.upload_image(path=f"influencers/{context.auth_user_id}", context=context, map_list={
            "image": "image"
        })

    def validate_image_key(self, context: PinfluencerContext):
        self.__common_before_hooks.validate_image_path(context=context, possible_paths=["image"])


class BrandBeforeHooks:

    def __init__(self, brand_validator: BrandValidator,
                 brand_repository: BrandRepository,
                 common_before_hooks: CommonBeforeHooks):
        self.__common_before_hooks = common_before_hooks
        self.__brand_repository = brand_repository
        self.__brand_validator = brand_validator

    def validate_auth_brand(self, context: PinfluencerContext):
        try:
            self.__brand_repository.load_for_auth_user(auth_user_id=context.auth_user_id)
        except NotFoundException as e:
            print_exception(e)
            context.short_circuit = True
            context.response.status_code = 404
            context.body = {}

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

    def upload_image(self, context: PinfluencerContext):
        self.__common_before_hooks.upload_image(path=f"brands/{context.auth_user_id}", context=context, map_list={
            "logo": "logo",
            "header-image": "header_image"
        })

    def validate_image_key(self, context: PinfluencerContext):
        self.__common_before_hooks.validate_image_path(context=context, possible_paths=["logo", "header_image"])


class BrandAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository,
                 common_after_common_hooks: CommonAfterHooks):
        self.__common_after_common_hooks = common_after_common_hooks
        self.__auth_user_repository = auth_user_repository

    def set_brand_claims(self, context: PinfluencerContext):
        user = User(auth_user_id=context.auth_user_id,
                    first_name=context.body["first_name"],
                    last_name=context.body["last_name"],
                    email=context.body["email"])
        self.__auth_user_repository.update_brand_claims(user=user)

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        self.__common_after_common_hooks.set_image_url(context=context,
                                                       image_fields=["header_image",
                                                                     "logo"],
                                                       collection=False)

    def tag_bucket_url_to_images_collection(self, context: PinfluencerContext):
        self.__common_after_common_hooks.set_image_url(context=context,
                                                       image_fields=["header_image",
                                                                     "logo"],
                                                       collection=True)


class InfluencerAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository,
                 common_after_hooks: CommonAfterHooks):
        self.__common_after_hooks = common_after_hooks
        self.__auth_user_repository = auth_user_repository

    def set_influencer_claims(self, context: PinfluencerContext):
        user = User(auth_user_id=context.auth_user_id,
                    first_name=context.body["first_name"],
                    last_name=context.body["last_name"],
                    email=context.body["email"])
        self.__auth_user_repository.update_influencer_claims(user=user)

    def tag_bucket_url_to_images(self, context: PinfluencerContext):
        self.__common_after_hooks.set_image_url(context=context,
                                                image_fields=["image"],
                                                collection=False)

    def tag_bucket_url_to_images_collection(self, context: PinfluencerContext):
        self.__common_after_hooks.set_image_url(context=context,
                                                image_fields=["image"],
                                                collection=True)


class UserBeforeHooks:

    def __init__(self, common_before_hooks: CommonBeforeHooks):
        self.__common_before_hooks = common_before_hooks

    def set_auth_user_id(self, context: PinfluencerContext):
        context.auth_user_id = context.event['requestContext']['authorizer']['jwt']['claims']['username']
        print(f"username {context.auth_user_id}")

    def set_categories_and_values(self, context: PinfluencerContext):
        self.__common_before_hooks.map_enums(context=context,
                                             key="values",
                                             enum_value=ValueEnum)
        self.__common_before_hooks.map_enums(context=context,
                                             key="categories",
                                             enum_value=CategoryEnum)


class UserAfterHooks:

    def __init__(self, auth_user_repository: AuthUserRepository,
                 common_after_hooks: CommonAfterHooks):
        self.__common_after_hooks = common_after_hooks
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

    def format_values_and_categories(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enums(context=context,
                                            key="values")
        self.__common_after_hooks.map_enums(context=context,
                                            key="categories")

    def format_values_and_categories_collection(self, context: PinfluencerContext):
        self.__common_after_hooks.map_enums_collection(context=context,
                                                       key="values")
        self.__common_after_hooks.map_enums_collection(context=context,
                                                       key="categories")


class HooksFacade:

    def __init__(self, common_hooks: CommonBeforeHooks,
                 brand_after_hooks: BrandAfterHooks,
                 influencer_after_hooks: InfluencerAfterHooks,
                 user_before_hooks: UserBeforeHooks,
                 user_after_hooks: UserAfterHooks,
                 influencer_before_hooks: InfluencerBeforeHooks,
                 brand_before_hooks: BrandBeforeHooks,
                 campaign_before_hooks: CampaignBeforeHooks,
                 campaign_after_hooks: CampaignAfterHooks):
        self.__campaign_before_hooks = campaign_before_hooks
        self.__brand_before_hooks = brand_before_hooks
        self.__influencer_before_hooks = influencer_before_hooks
        self.__user_after_hooks = user_after_hooks
        self.__influencer_after_hooks = influencer_after_hooks
        self.__user_before_hooks = user_before_hooks
        self.__brand_after_hooks = brand_after_hooks
        self.__common_before_hooks = common_hooks
        self.__campaign_after_hooks = campaign_after_hooks

    def get_campaign_after_hooks(self) -> CampaignAfterHooks:
        return self.__campaign_after_hooks

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
