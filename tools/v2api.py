from chronos.settings import CHRONOS_API as API
from tools.utils import request_json


def get_api_url(key, **kwargs):
    return API['base_url'] + API['urls'][key].format(**kwargs)


def get_rooms_under(parent_id):
    """
    Get rooms under the parent_id room.
    """
    url = get_api_url('room_under', rootId=parent_id)
    json = request_json(url)
    return json


def get_root_rooms():
    """
    Get all root rooms.
    """
    url = get_api_url('room_get_roots')
    json = request_json(url)
    return json