from datetime import datetime, timedelta
import json
import locale
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
import time

from synonyms import Semester
from thabella_api import Schedule

schedule = Schedule()
synonyms_semester = Semester()


class APICall:
    def __init__(self):
        self._error = ''

    def _get_shortcut(self, slot_degree_course):
        with open('shortcuts.json', 'r') as file:
            shortcuts = json.loads(file.read())

        shortcut = 'not found'
        for i in range(len(shortcuts)):
            if str(slot_degree_course).lower() == shortcuts[i][0]:
                shortcut = shortcuts[i][1]
                break

        if shortcut == 'not found':
            self._error = 'Ich konnte diesen Studiengang an der THD leider nicht finden.'
        return shortcut

    @staticmethod
    def _get_date(slot_date):
        date = str(slot_date).lower()
        if date == 'morgen':
            date = datetime.now() + timedelta(1)
        elif date == 'montag' or date == 'dienstag' or date == 'mittwoch' or date == 'donnerstag' or date == 'freitag' \
                or date == 'samstag' or date == 'sonntag':
            for i in range(1, 7):
                if date == 'montag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 1:
                        date = datetime.now() + timedelta(i)
                if date == 'dienstag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 2:
                        date = datetime.now() + timedelta(i)
                if date == 'mittwoch':
                    if (datetime.now() + timedelta(i)).isoweekday() == 3:
                        date = datetime.now() + timedelta(i)
                if date == 'donnerstag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 4:
                        date = datetime.now() + timedelta(i)
                if date == 'freitag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 5:
                        date = datetime.now() + timedelta(i)
                if date == 'samstag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 6:
                        date = datetime.now() + timedelta(i)
                if date == 'sonntag':
                    if (datetime.now() + timedelta(i)).isoweekday() == 7:
                        date = datetime.now() + timedelta(i)

        elif len(date) <= 5 and date.find('.') != -1:
            date += time.strftime(".%Y")
            date = datetime.strptime(date, "%d.%m.%Y")

        elif 6 <= len(date) <= 10 and date.find('.') != -1 and date[3:].find('.') != -1:
            if len(date) <= 8:
                date = f'{date[:-2]}20{date[-2:]}'
            date = datetime.strptime(date, "%d.%m.%Y")

        else:
            date = datetime.now()

        locale.setlocale(locale.LC_ALL, "de_DE")
        return date.strftime("%A, %d. %B %Y")

    def _get_semester(self, slot_semester):
        semester = synonyms_semester.get_semester(slot_semester)
        if semester == 'key error':
            self._error = 'Bitte gib ein gültiges Semester ein. Es muss zwischen 1 und 7 sein.'
        return semester

    def make_request(self, slot_degree_course, slot_date, slot_semester):
        date = self._get_date(slot_date)
        shortcut = self._get_shortcut(slot_degree_course)
        semester = self._get_semester(slot_semester)

        if self._error != '':
            tmp_error = self._error
            self._error = ''
            return tmp_error

        course_and_semester = shortcut + semester
        schedule.get_classes(course_and_semester, date)
        return self._error


api_call = APICall()


class ActionGetClass(Action):
    def name(self):
        return "action_get_class"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        error = api_call.make_request(tracker.get_slot('degree_course'), tracker.get_slot('date'),
                                      tracker.get_slot('semester'))
        # error handling
        if error != '':
            dispatcher.utter_message(text=error)
            return []

        # search for class and give an answer
        next_class = self._search_for_class(tracker.get_slot('time'), tracker.get_slot('date'))
        dispatcher.utter_message(text=next_class)
        return []

    @staticmethod
    def _search_for_class(slot_time=None, slot_date=None):
        with open('classes.json', 'r') as file:
            classes = json.loads(file.read())
        date = str(slot_date).lower()
        current_time = datetime.now().strftime("%H:%M")

        if len(classes) >= 1:
            date_first_day = classes[0]['startDateTime'][:10]
        else:
            return 'Es sieht so aus als hättest du keine Vorlesungen'

        # search for classes without any given time
        if slot_time is None:
            list_of_lectures = []
            for i in range(len(classes)):
                # no more classes on this day
                if classes[i]['startDateTime'][:10] != date_first_day:
                    break
                # classes for today
                if date == 'heute' or date is None:
                    if classes[i]['startDateTime'][11:] >= current_time:
                        list_of_lectures.append(classes[i]['description'])
                # classes for a specific day e.g. on monday
                else:
                    list_of_lectures.append(classes[i]['description'])

            if len(list_of_lectures) == 0:
                return 'Du hast keine Vorlesungen'
            else:
                list_of_lectures = list(set(list_of_lectures))
                text = 'Du hast '
                for i in range(len(list_of_lectures)):
                    text = text + list_of_lectures[i] + ', '
                return text[:-2]

        # search for class at a certain time
        else:
            for i in range(len(classes)):
                # only search today for the class otherwise stop
                if classes[i]['startDateTime'][:10] != date_first_day:
                    break
                if classes[i]['startDateTime'][11:] == slot_time:
                    return f"Du hast {classes[i]['description']}"
        return 'Du hast keine Vorlesungen'


class ActionGetTime(Action):
    def name(self):
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        error = api_call.make_request(tracker.get_slot('degree_course'), tracker.get_slot('date'),
                                      tracker.get_slot('semester'))
        # error handling
        if error != '':
            dispatcher.utter_message(text=error)
            return []

        # search for time of the class and give an answer
        time_of_class = self._search_for_time(tracker.get_slot('lecture'), tracker.get_slot('date'))
        dispatcher.utter_message(text=time_of_class)
        return []

    @staticmethod
    def _search_for_time(slot_lecture=None, slot_date=None):
        with open('classes.json', 'r') as file:
            classes = json.loads(file.read())

        # no classes
        if len(classes) == 0:
            return 'Du hast frei'

        # search for next class without any given lecture
        current_time = datetime.now().strftime("%H:%M")
        if slot_lecture is None:
            if slot_date is None or str(slot_date).lower() == 'heute':
                for i in range(len(classes)):
                    if classes[i]['startDateTime'][11:] >= current_time:
                        return f"{classes[i]['description']} beginnt um {classes[i]['startDateTime'][11:]} Uhr"
            else:
                return f"Du hast {classes[0]['description']} um {classes[0]['startDateTime'][11:]} Uhr"
        else:
            # search for the time of a given lecture
            for i in range(len(classes)):
                if str(classes[i]['description']).lower() == str(slot_lecture).lower():
                    return f"{classes[i]['description']} beginnt um {classes[i]['startDateTime'][11:]} Uhr"
        return 'Ich konnte keine Uhrzeit für die Vorlesung finden'


class ActionGetLocation(Action):
    def name(self):
        return "action_get_location"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        error = api_call.make_request(tracker.get_slot('degree_course'), tracker.get_slot('date'),
                                      tracker.get_slot('semester'))
        # error handling
        if error != '':
            dispatcher.utter_message(text=error)
            return []

        # search for location of the class and give an answer
        location_of_class = self._search_for_location(tracker.get_slot('lecture'), tracker.get_slot('date'))
        dispatcher.utter_message(text=location_of_class)
        return []

    @staticmethod
    def _search_for_location(slot_lecture=None, slot_date=None):
        with open('classes.json', 'r') as file:
            classes = json.loads(file.read())

        # no classes
        if len(classes) == 0:
            return 'Du hast frei'

        # search for next class without any given lecture
        current_time = datetime.now().strftime("%H:%M")
        if slot_lecture is None:
            if slot_date is None or str(slot_date).lower() == 'heute':
                for i in range(len(classes)):
                    if classes[i]['startDateTime'][11:] >= current_time:
                        room = list(classes[i]['room_ident'].values())
                        return f"{classes[i]['description']} findet in Raum {room[0]} statt"
            else:
                room = list(classes[0]['room_ident'].values())
                return f"Die Vorlesung {classes[0]['description']} findet in Raum {room[0]} statt"
        else:
            # search for the time of a given lecture
            for i in range(len(classes)):
                if str(classes[i]['description']).lower() == str(slot_lecture).lower():
                    room = list(classes[i]['room_ident'].values())
                    return f"{classes[i]['description']} findet in Raum {room[0]} statt"
        return 'Ich konnte keinen Raum für die Vorlesung finden'
