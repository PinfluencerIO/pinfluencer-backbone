from src.data_access_layer import to_list
from src.data_access_layer.product import Product
from src.interfaces.data_manager_interface import DataManagerInterface
from src.web.filters import FilterChain
from src.web.http_util import PinfluencerResponse
from src.web.processors import ProcessInterface
from src.web.processors.hacks import old_manual_functions


# Todo: Implement all these processors


class ProcessPublicProducts(ProcessInterface):
    def __init__(self, data_manager: DataManagerInterface):
        super().__init__(data_manager)

    def do_process(self, event: dict) -> PinfluencerResponse:
        print(self)
        return PinfluencerResponse(body=to_list(self._data_manager.session.query(Product).all()))


class ProcessPublicGetProductBy(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        self.filter.do_chain(event)
        return old_manual_functions.get_product_by_id(event)


class ProcessAuthenticatedGetProductById(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        self.filter.do_chain(event)
        return old_manual_functions.get_product_by_id(event)


class ProcessAuthenticatedGetProduct(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        self.filter.do_chain(event)
        return old_manual_functions.get_authenticated_products(event)


class ProcessAuthenticatedPostProduct(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        print(self)
        self.filter.do_chain(event)
        return old_manual_functions.create_authenticated_product(event)


class ProcessAuthenticatedPutProduct(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        print(self)
        self.filter.do_chain(event)
        return old_manual_functions.update_authenticated_product(event)


class ProcessAuthenticatedDeleteProduct(ProcessInterface):
    def __init__(self, filter_chain: FilterChain):
        self.filter = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        print(self)
        self.filter.do_chain(event)
        return old_manual_functions.delete_authenticated_product(event)


class ProcessAuthenticatedPatchProductImage(ProcessInterface):
    def __init__(self, filter_chain: FilterChain) -> None:
        self.filters = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        self.filters.do_chain(event)
        return old_manual_functions.patch_product_image(event)


class ProcessAuthenticatedPatchBrandImage(ProcessInterface):
    def __init__(self, filter_chain: FilterChain) -> None:
        self.filters = filter_chain

    def do_process(self, event: dict) -> PinfluencerResponse:
        self.filters.do_chain(event)
        return old_manual_functions.patch_brand_image(event)
