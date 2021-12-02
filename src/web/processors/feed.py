from src.data_access_layer import to_list
from src.data_access_layer.brand import Brand
from src.data_access_layer.product import Product
from src.interfaces.data_manager_interface import DataManagerInterface
from src.pinfluencer_response import PinfluencerResponse
from src.web.processors import ProcessInterface


class ProcessPublicFeed(ProcessInterface):
    def __init__(self, data_manager: DataManagerInterface):
        super().__init__(data_manager)

    def do_process(self, event: dict) -> PinfluencerResponse:
        brands: list[Brand] = self._data_manager.session.query(Brand.id).all()
        products = []
        for brand in brands:
            products.extend(self._data_manager.session
                            .query(Product)
                            .filter(Product.brand_id == brand.id)
                            .limit(3)
                            .all())
        return PinfluencerResponse(body=to_list(products[:20]))
