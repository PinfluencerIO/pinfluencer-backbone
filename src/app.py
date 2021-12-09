from collections import OrderedDict

from src.container import Container
from src.data_access_layer.read_data_access import load_product_by_id_owned_by_brand, load_brands, \
    load_max_3_products_for_brand, load_all_products_for_brand_id
from src.data_access_layer.write_data_access import update_brand_image, write_new_product, update_new_product, \
    patch_product_image, delete_product
from src.filters.payload_validation import *
from src.log_util import print_exception
from src.processors.create_brand_for_authenticated_user import ProcessAuthenticatedPostBrand
from src.processors.feed import ProcessPublicFeed
from src.processors.get_brand_for_authenticated_user import ProcessAuthenticatedGetBrand
from src.processors.get_brands import ProcessPublicBrands
from src.processors.get_brands_by_id import ProcessPublicGetBrandBy
from src.processors.get_products_for_brand import ProcessPublicAllProductsForBrand
from src.processors.products import *
from src.processors.update_brand_for_authenticated_user import ProcessAuthenticatedPutBrand
from src.processors.update_image_for_brand_of_authenticated_user import ProcessAuthenticatedPatchBrandImage


def lambda_handler(event, context):
    container = Container()
    try:
        routes = OrderedDict({
            # public endpoints
            'GET /feed': ProcessPublicFeed(load_brands, load_max_3_products_for_brand, container.data_manager),

            'GET /brands': ProcessPublicBrands(load_brands, container.data_manager),

            'GET /brands/{brand_id}': ProcessPublicGetBrandBy(LoadResourceById(container.data_manager, 'brand')),

            'GET /brands/{brand_id}/products': ProcessPublicAllProductsForBrand(
                LoadResourceById(container.data_manager, 'brand'), load_all_products_for_brand_id, container.data_manager),

            'GET /products': ProcessPublicProducts(container.data_manager),

            'GET /products/{product_id}': ProcessPublicGetProductBy(LoadResourceById(container.data_manager, 'product'),
                                                                    container.data_manager),

            # authenticated brand endpoints
            'GET /brands/me': ProcessAuthenticatedGetBrand(container.get_brand_associated_with_cognito_user,
                                                           container.data_manager),

            'POST /brands/me': ProcessAuthenticatedPostBrand(NoBrandAssociatedWithCognitoUser(container.data_manager),
                                                             BrandPostPayloadValidation(), container.data_manager),

            'PUT /brands/me': ProcessAuthenticatedPutBrand(container.get_brand_associated_with_cognito_user,
                                                           BrandPutPayloadValidation(),
                                                           container.data_manager),

            'PATCH /brands/me/image': ProcessAuthenticatedPatchBrandImage(
                container.get_brand_associated_with_cognito_user,
                BrandImagePatchPayloadValidation(),
                update_brand_image,
                container.data_manager),

            # authenticated product endpoints
            'GET /products/me': ProcessAuthenticatedGetProducts(container.get_brand_associated_with_cognito_user,
                                                                load_all_products_for_brand_id,
                                                                container.data_manager),

            'GET /products/me/{product_id}': ProcessAuthenticatedGetProductById(
                container.get_brand_associated_with_cognito_user,
                load_product_by_id_owned_by_brand,
                container.data_manager),

            'POST /products/me': ProcessAuthenticatedPostProduct(
                container.get_brand_associated_with_cognito_user,
                ProductPostPayloadValidation(),
                write_new_product,
                container.data_manager),

            'PUT /products/me/{product_id}': ProcessAuthenticatedPutProduct(
                container.get_brand_associated_with_cognito_user,
                ProductPutPayloadValidation(),
                update_new_product,
                container.data_manager),

            'PATCH /products/me/{product_id}/image': ProcessAuthenticatedPatchProductImage(
                container.get_brand_associated_with_cognito_user,
                ProductImagePatchPayloadValidation(),
                patch_product_image,
                container.data_manager),

            'DELETE /products/me/{product_id}': ProcessAuthenticatedDeleteProduct(
                container.get_brand_associated_with_cognito_user,
                delete_product,
                container.data_manager),
        })

        print(f'route: {event["routeKey"]}')
        print(f'event: {event}')

        processor: ProcessInterface = routes[event['routeKey']]
        print(f'process: {processor}')

        response: PinfluencerResponse = processor.do_process(event)
        return response.as_json()
    except KeyError as ke:
        print(f'Missing required key {ke}')
        return PinfluencerResponse.as_400_error().as_json()
    except Exception as e:
        print_exception(e)
        return PinfluencerResponse.as_500_error().as_json()
