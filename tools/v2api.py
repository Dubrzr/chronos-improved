from chronos.settings import CHRONOS_API as API
from datetime import datetime
from tools.utils import request_json

from chronos.settings import CHRONOS_API


def get_api_url(key, **kwargs):
    return API['base_url'] + API['urls'][key].format(**kwargs)


def pdate(date_str):
    date = datetime.strptime(date_str, CHRONOS_API['date_format'])
    date += CHRONOS_API['tz_delta']
    return date


def get_rooms_under(parent_id):
    """
    Get rooms under the parent_id room.
    """
    url = get_api_url('room_under',
                      rootId=parent_id)
    json = request_json(url)
    return json


def get_root_rooms():
    """
    Get all root rooms.
    """
    url = get_api_url('room_get_roots')
    json = request_json(url)
    return json


def get_week(week_id, entity_id, entity_type_id):
    """
    Get the week corresponding to the given week, entity and entity type
    identifiers.
    """
    url = get_api_url('week_get',
                      weekId=week_id,
                      entityId=entity_id,
                      entityTypeId=entity_type_id)
    json = request_json(url)
    return json


def get_current_week(entity_id, entity_type_id):
    """
    Get the current week id.
    """
    url = get_api_url('week_current',
                      entityId=entity_id,
                      entityTypeId=entity_type_id)
    json = request_json(url)
    return json


def get_current_week_id():
    """
    Get the current week id.
    """
    return get_current_week(0, 0)['Id']