from collections import OrderedDict

from src.common.log_util import print_exception
from src.services import Container
from src.web.filters import *
from src.web.processors.brands import *
from src.web.processors.feed import *
from src.web.processors.products import *


def lambda_handler(event, context):
    container = Container()
    try:
        routes = OrderedDict({
            # public endpoints
            'GET /feed': ProcessPublicFeed(container.data_manager),
            'GET /brands': ProcessPublicBrands(container.data_manager),
            'GET /brands/{brand_id}': ProcessPublicGetBrandBy(FilterChainImp([container.valid_brand_filter]),
                                                              container.data_manager),
            'GET /brands/{brand_id}/products': ProcessPublicAllProductsForBrand(
                FilterChainImp([container.valid_brand_filter]),
                container.data_manager),
            'GET /products': ProcessPublicProducts(container.data_manager),
            'GET /products/{product_id}': ProcessPublicGetProductBy(
                FilterChainImp([container.valid_product_filter]),
                container.data_manager),

            # authenticated brand endpoints
            'GET /brands/me': ProcessAuthenticatedGetBrand(FilterChainImp([container.auth_filter]),
                                                           container.data_manager),
            'POST /brands/me': ProcessAuthenticatedPostBrand(
                FilterChainImp([OneTimeCreateBrandFilter(container.data_manager),
                                BrandPostPayloadValidation()]),
                container.data_manager, container.image_repository, container.status_manager),
            'PUT /brands/me': ProcessAuthenticatedPutBrand(FilterChainImp([container.auth_filter,
                                                                           BrandPutPayloadValidation()]),
                                                           container.data_manager, container.status_manager),
            'PATCH /brands/me/image': ProcessAuthenticatedPatchBrandImage(
                FilterChainImp([container.auth_filter, BrandImagePatchPayloadValidation()]),
                container.data_manager,
                container.image_repository, container.status_manager),

            # authenticated product endpoints
            'GET /products/me': ProcessAuthenticatedGetProduct(FilterChainImp([container.auth_filter]),
                                                               container.data_manager),
            'GET /products/me/{product_id}': ProcessAuthenticatedGetProductById(
                FilterChainImp([container.auth_filter, container.valid_product_filter, OwnerOnly('product')]),
                container.data_manager),
            'POST /products/me': ProcessAuthenticatedPostProduct(
                FilterChainImp([container.auth_filter, ProductPostPayloadValidation()]),
                container.data_manager, container.image_repository, container.status_manager),
            'PUT /products/me/{product_id}': ProcessAuthenticatedPutProduct(
                FilterChainImp(
                    [container.auth_filter, container.valid_product_filter, OwnerOnly('product'),
                     ProductPutPayloadValidation()]), container.data_manager, container.status_manager),
            'PATCH /products/me/{product_id}/image': ProcessAuthenticatedPatchProductImage(FilterChainImp(
                [container.auth_filter, container.valid_product_filter, OwnerOnly('product'),
                 ProductImagePatchPayloadValidation()]), container.image_repository, container.data_manager,
                container.status_manager),
            'DELETE /products/me/{product_id}': ProcessAuthenticatedDeleteProduct(
                FilterChainImp([container.auth_filter, container.valid_product_filter, OwnerOnly('product')]),
                container.data_manager, container.image_repository, container.status_manager),
        })
        print(f'route: {event["routeKey"]}')
        print(f'event: {event}')
        processor: ProcessInterface = routes[event['routeKey']]
        print("start run filters")
        processor.run_filters(event)
        print("finished run filters")
        print("start run processor")
        response = processor.do_process(event).as_json()
        print("finished run processor")
        container.status_manager.status = True
        return response
    except KeyError as ke:
        print(f'Missing required key {ke}')
        return PinfluencerResponse.as_400_error().as_json()
    except NotFoundById:
        print(f'NotFoundById')
        return PinfluencerResponse.as_404_error().as_json()
    except NotFoundByAuthUser as e:
        print(f'NotFoundByAuthUser')
        return PinfluencerResponse.as_401_error(str(e)).as_json()
    except OwnershipError as ownership:
        return PinfluencerResponse.as_401_error(str(ownership)).as_json()
    except InvalidId:
        print(f'InvalidId')
        return PinfluencerResponse.as_400_error().as_json()
    except PayloadValidationError:
        print(f'BrandPayloadValidationError')
        return PinfluencerResponse.as_400_error().as_json()
    except BrandAlreadyCreatedForAuthUser:
        print(f'BrandAlreadyCreatedForAuthUser')
        return PinfluencerResponse.as_400_error('There is already a brand associated with this auth user').as_json()
    except Exception as e:
        print_exception(e)
        return PinfluencerResponse.as_500_error().as_json()
    finally:
        container.data_manager.cleanup()
