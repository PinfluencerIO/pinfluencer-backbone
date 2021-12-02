import uuid

import pytest

from src.data_access_layer.product import Product
from src.filters import FilterChainImp, NotFoundById
from src.filters.valid_id_filters import LoadResourceById
from src.web.http_util import PinfluencerResponse
from src.web.processors.products import ProcessPublicGetProductBy
from tests.unit import FakeDataManager, product_generator, brand_generator


@pytest.fixture()
def get_public_product_by_id_fixture():
    data_manager = FakeDataManager()
    product_processor = ProcessPublicGetProductBy(data_manager=data_manager,
                                                  filter_chain=FilterChainImp(
                                                      [LoadResourceById(data_manager, 'product')]))
    return product_processor, data_manager


class TestPublicProductById:
    __result: PinfluencerResponse
    __products: list[Product]
    __product_processor: ProcessPublicGetProductBy
    __data_manager: FakeDataManager
    __event: dict

    def __setup(self, get_public_product_by_id_fixture, callback=lambda *args: None):
        (self.__product_processor, self.__data_manager) = get_public_product_by_id_fixture
        callback()
        self.__product_processor.run_filters(event=self.__event)
        self.__result = self.__product_processor.do_process(self.__event)

    def __setup_test_data(self):
        brands = [brand_generator(1)]
        self.__products = [
            product_generator(1, brands[0].id)
        ]
        self.__data_manager.create_fake_data(brands)
        self.__data_manager.create_fake_data(self.__products)
        self.__products[0].brand = brands[0]
        self.__event = {
            'pathParameters': {
                'product_id': self.__products[0].id
            }
        }

    def __setup_empty_data(self):
        self.__event = {
            'pathParameters': {
                'product_id': str(uuid.uuid4())
            }
        }

    def off_test_correct_product_is_found_when_product_is_in_db(self, get_public_product_by_id_fixture):
        self.__setup(get_public_product_by_id_fixture=get_public_product_by_id_fixture, callback=self.__setup_test_data)
        assert self.__result.is_ok()
        assert self.__result.body == self.__products[0].as_dict()

    def off_test_no_product_is_found_when_product_is_not_in_db(self, get_public_product_by_id_fixture):
        with pytest.raises(NotFoundById):
            self.__setup(get_public_product_by_id_fixture=get_public_product_by_id_fixture,
                         callback=self.__setup_empty_data)
