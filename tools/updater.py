from concurrent.futures import ThreadPoolExecutor, as_completed
import functools
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
import time

from chronos.models import Lesson, Room
from chronos.settings import ASYNC_MAX_WORKERS, CHRONOS_API
from tools.v2api import get_rooms_under, get_root_rooms, get_current_week,\
    get_current_week_id, get_week, pdate


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


@transaction.atomic
def update_under_rooms():
    """
    Get and create rooms that are under known root rooms
    """
    # First delete all non root rooms
    Room.objects.filter(root__isnull=False).delete()

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

def timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        print('function [{}] finished in {} ms'.format(
            func.__name__, int(elapsedTime * 1000)))
    return newfunc

@timeit
@transaction.atomic
def update_lessons():
    """
    Get and create lessons that are under known rooms
    """
    # First delete all existing lessons
    Lesson.objects.all().delete()

    def create(lesson):
        try:
            l = Lesson.objects.get(api_id=lesson['Id'])
            # [Handle API changes]
            # If the name of the room changed, update it
            if l.name != lesson['Name']:
                l.name = lesson['Name']
                l.save()
        except ObjectDoesNotExist:
            l = Lesson(api_id=lesson['Id'],
                       name=lesson['Name'],
                       duration=lesson['Duration'],
                       start_date=pdate(lesson['BeginDate']),
                       end_date=pdate(lesson['EndDate']))
            l.save()
            print('Add lesson: {}'.format(l.name))
        for room in lesson['RoomList']:
            try:
                r = Room.objects.get(api_id=room['Id'])
                l.rooms.add(r)
            except:
                pass


    def treat_week(room, days):
        for day in days:
            for lesson in day['CourseList']:
                # API is returning not corresponding courses to room
                # -> continue on wrong data
                if room.api_id not in [r['Id'] for r in lesson['RoomList']]:
                    continue
                create(lesson)

    week_id = get_current_week_id()
    with ThreadPoolExecutor(max_workers=ASYNC_MAX_WORKERS) as executor:
        fs = { executor.submit(get_week, week_id, room.api_id, 3): room
               for room in Room.objects.filter(root__isnull=False) }
        for future in as_completed(fs): # yield as soon as completed
            room = fs[future]
            try:
                days = future.result()['DayList']
            except Exception:
                days = []
            treat_week(room, days)
