from abc import ABC, abstractmethod
import json

import requests


class JobSiteAPI(ABC):
    @abstractmethod
    def get_vacanies(self, filter_word):
        pass

class HeadHunterAPI(JobSiteAPI):
    def __init__(self):
        pass

    def get_vacanies(self, filter_word):
        #for page in range(0, 5):
        params = {
            'text': f'NAME:{filter_word}',  # Текст фильтра. В имени должно быть слово "Аналитик"
            #'page': page,  # Индекс страницы поиска на HH
            'per_page': 50  # Кол-во вакансий на 1 странице
        }

        req = requests.get('https://api.hh.ru/vacancies', params)  # Посылаем запрос к API
        jsObj = json.loads(req.content.decode())  # Декодируем его ответ, чтобы Кириллица отображалась корректно
        req.close()
        return jsObj


class SuperJobAPI(JobSiteAPI):
    def get_vacanies(self, filter_word):

hh=HeadHunterAPI()
