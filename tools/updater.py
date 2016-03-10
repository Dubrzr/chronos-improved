from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from chronos.models import Lesson, Room
from tools.v2api import get_api_url, get_rooms_under, get_root_rooms


def update_root_rooms(room_names=None):
    """
    Get and create root rooms if they do not exist
    :param room_names: If not None, limits update to only room_names
    """
    for room in get_root_rooms():
        if room_names is not None and room['Name'] not in room_names:
            continue
        try:
            r = Room.objects.get(api_id=room['Id'])
            # [Handle API changes]
            # If the id already exist but is not associated with a root room
            # we just delete it and create a new one, but as a root room
            if r.root is not None:
                r.delete()
                raise ObjectDoesNotExist()

            # [Handle API changes]
            # If the name of the room changed, update it
            if r.name != room['Name']:
                r.name = room['Name']
                r.save()
        except ObjectDoesNotExist:
            try:
                Room(api_id=room['Id'], name=room['Name']).save()
            except IntegrityError as e:
                if 'unique constraint' in e.message:
                    # TODO: log it
                    pass


def update_under_rooms():
    """
    Get and create rooms that are under root rooms
    """
    root_rooms = list(Room.objects.filter(root=None))
    ll = { str(room.id): get_rooms_under(room.api_id) for room in root_rooms }

    for root_room_id, l in ll.items():
        for room in l:
            if room['ParentId'] == -1:
                continue
            try:
                r = Room.objects.get(api_id=room['Id'])
                # [Handle API changes]
                # If the id already exist but is associated with a root room
                # we just delete it and create a new one, but as an under room
                if r.root is None:
                    r.delete()
                    raise ObjectDoesNotExist()

                # [Handle API changes]
                # If the id already exist but is not under the right root room
                # we just delete it and create a new one
                if r.root.id != root_room_id:
                    r.delete()
                    raise ObjectDoesNotExist()

                # [Handle API changes]
                # If the name of the room changed, update it
                if r.name != room['Name']:
                    r.name = room['Name']
                    r.save()
            except ObjectDoesNotExist:
                try:
                    Room(api_id=room['Id'],
                         name=room['Name'],
                         parent_api_id=room['ParentId'],
                         root_id=root_room_id).save()
                except IntegrityError as e:
                    if 'unique constraint' in e.message:
                        # TODO: log it
                        pass

