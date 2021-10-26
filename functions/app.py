from functions.log_util import print_exception
from functions.processors.brands import *
from functions.processors.feed import ProcessPublicFeed
from functions.processors.products import *

from functions.web.filters import FilterChainImp, ValidBrandId, ValidProductId, AuthFilter, \
    BrandPostPayloadValidation, PayloadValidationError, NotFoundByAuthUser, OneTimeCreateBrandFilter, \
    BrandAlreadyCreatedForAuthUser, ProductPostPayloadValidation, OwnerOnly, OwnershipError, NotFoundById, InvalidId
from functions.web.http_util import PinfluencerResponse
from collections import OrderedDict


def lambda_handler(event, context):
    try:
        print(f'route: {event["routeKey"]}')
        print(f'event: {event}')
        return routes[event['routeKey']].do_process(event).as_json()
    except KeyError as ke:
        print(f'Missing required key {ke}')
        return PinfluencerResponse.as_400_error().as_json()
    except NotFoundById:
        print(f'NotFoundById')
        return PinfluencerResponse.as_404_error().as_json()
    except NotFoundByAuthUser:
        print(f'NotFoundByAuthUser')
        return PinfluencerResponse.as_401_error().as_json()
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


routes = OrderedDict(
    {
        # public endpoints
        'GET /feed': ProcessPublicFeed(),
        'GET /brands': ProcessPublicBrands(),
        'GET /brands/{brand_id}': ProcessPublicGetBrandBy(FilterChainImp([ValidBrandId()])),
        'GET /brands/{brand_id}/products': ProcessPublicAllProductsForBrand(FilterChainImp([ValidBrandId()])),
        'GET /products': ProcessPublicProducts(),
        'GET /products/{product_id}': ProcessPublicGetProductBy(FilterChainImp([ValidProductId()])),

        # authenticated brand endpoints
        'GET /brands/me': ProcessAuthenticatedGetBrand(FilterChainImp([(AuthFilter())])),
        'POST /brands/me': ProcessAuthenticatedPostBrand(
            FilterChainImp([OneTimeCreateBrandFilter(), BrandPostPayloadValidation()])),
        'PUT /brands/me': ProcessAuthenticatedPutBrand(FilterChainImp([AuthFilter(), BrandPostPayloadValidation()])),

        # authenticated product endpoints
        'GET /products/me': ProcessAuthenticatedGetProduct(FilterChainImp([AuthFilter()])),
        'GET /products/me/{product_id}': ProcessAuthenticatedGetProductById(
            FilterChainImp([AuthFilter(), ValidProductId(), OwnerOnly('product')])),
        'POST /products/me': ProcessAuthenticatedPostProduct(
            FilterChainImp([AuthFilter(), ProductPostPayloadValidation()])),
        'PUT /products/me/{product_id}': ProcessAuthenticatedPutProduct(
            FilterChainImp([AuthFilter(), ValidProductId(), OwnerOnly('product'), ProductPostPayloadValidation()])),
        'DELETE /products/me/{product_id}': ProcessAuthenticatedDeleteProduct(
            FilterChainImp([AuthFilter(), ValidProductId(), OwnerOnly('product')])),
    }
)
