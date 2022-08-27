import json
import requests


# Parameters must have the following format for the api to work:
# course and semester: 'KI-3'
# date: 'Montag, 01. Dezember 2021'

class Schedule:
    def __init__(self):
        self._url = 'https://thabella.th-deg.de/thabella/opn/period/findByOrgPartDate'
        self._body = {'description': "",
                      'organiser': "",
                      'participants': '',
                      'rooms': "0",
                      'startDate': ''
                      }

    @staticmethod
    def _delete(data, start_date):
        # convert date to correct format
        elements = start_date.split(' ')
        year = elements[3]
        month = {'Januar': '01',
                 'Februar': '02',
                 'März': '03',
                 'April': '04',
                 'Mai': '05',
                 'Juni': '06',
                 'Juli': '07',
                 'August': '08',
                 'September': '09',
                 'Oktober': '10',
                 'November': '11',
                 'Dezember': '12',
                 }[elements[2]]
        day = elements[1][:-1]
        date_formatted = year + '-' + month + '-' + day

        # delete all entries before the formatted date
        start = 0
        for i in range(len(data)):
            date = data[i]['startDateTime'][:10]
            if date == date_formatted:
                start = i
                return data[start:]
        return []

    def _get_data(self, course_and_semester, start_date):
        self._body['participants'] = course_and_semester
        self._body['startDate'] = start_date

        resp = requests.post(url=self._url, json=self._body)
        return self._delete(resp.json(), start_date)

    def get_classes(self, course_and_semester, start_date):
        data = self._get_data(course_and_semester, start_date)

        with open('classes.json', 'w') as f:
            f.write(json.dumps(data, indent=4))
