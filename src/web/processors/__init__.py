import abc

from src.interfaces.data_manager_interface import DataManagerInterface
from src.web.http_util import PinfluencerResponse


# Todo: Not sure this is the right place for an interface...read up about it.


class ProcessInterface(abc.ABC):
    _data_manager: DataManagerInterface

    def __init__(self, data_manager: DataManagerInterface):
        self._data_manager = data_manager

    @abc.abstractmethod
    def do_process(self, event: dict) -> PinfluencerResponse:
        pass


def get_user(event):
    return event['requestContext']['authorizer']['jwt']['claims']['cognito:username']
