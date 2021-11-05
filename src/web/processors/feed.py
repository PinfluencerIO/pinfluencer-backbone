from src.interfaces.contract.product_repository_interface import ProductRepositoryInterface
from src.web.processors import ProcessInterface
from src.web.processors.base_processor import BaseProcessor
from src.web.processors.hacks import old_manual_functions
from src.web.http_util import PinfluencerResponse


class ProcessPublicFeed(ProcessInterface, BaseProcessor):
    def __init__(self):
        super().__init__()

    def do_process(self, event: dict) -> PinfluencerResponse:
        print(self)
        return old_manual_functions.get_feed()