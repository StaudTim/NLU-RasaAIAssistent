class Semester:
    def __init__(self):
        self._myDict = {}

        for k in ['1', 'eins', 'ersten', 'erstem', 'erstes', 'erste']:
            self._myDict[k] = '1'

        for k in ['2', 'zwei', 'zweiten', 'zweitem', 'zweites', 'zweite']:
            self._myDict[k] = '2'

        for k in ['3', 'drei', 'dritten', 'drittem', 'drittes', 'dritte']:
            self._myDict[k] = '3'

        for k in ['4', 'vier', 'vierten', 'viertem', 'viertes', 'vierte']:
            self._myDict[k] = '4'

        for k in ['5', 'fünf', 'fünften', 'fünftem', 'fünftes', 'fünfte']:
            self._myDict[k] = '5'

        for k in ['6', 'sechs', 'sechsten', 'sechstem', 'sechstes', 'sechste']:
            self._myDict[k] = '6'

        for k in ['7', 'sieben', 'siebten', 'siebtem', 'siebtes', 'siebte']:
            self._myDict[k] = '7'

    def get_semester(self, k):
        try:
            return self._myDict[k]
        except KeyError:
            return 'key error'
