from bs4 import BeautifulSoup
import json
import requests


def get_shortcuts():
    url = 'https://www.th-deg.de/studienfelder'

    # get sourcecode from the website
    response = requests.get(url)
    html = BeautifulSoup(response.text, 'html.parser')

    # find information in html
    html_filtered = html.find_all('div', class_='card h-100 hover_studienprogram')
    quotes_description = html.find_all('p', class_='card-text')

    shortcut = []
    for i in range(len(html_filtered)):
        element = html_filtered[i].find('a', href=True)
        link = element['href'][1:]
        if link[-1] == 'b' or link[-1] == 'm' and link[-2] == '-':
            link = link[:-1]
        shortcut.append(link)

    # collect descriptions in a list
    descriptions = []
    for element in quotes_description:
        descriptions.append(str(element.text).strip().lower())

    # combine lists and write in json file
    all_shortcuts = list(zip(descriptions, shortcut))
    remove = []
    for i in range(len(all_shortcuts)):
        if len(all_shortcuts[i][1]) > 5:
            remove.append(all_shortcuts[i])

    shortcuts = list(set([item for item in all_shortcuts if item not in remove]))
    shortcuts.sort()

    with open('shortcuts.json', 'w') as f:
        f.write(json.dumps(shortcuts, indent=4))


if __name__ == "__main__":
    get_shortcuts()
