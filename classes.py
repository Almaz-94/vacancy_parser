from abc import ABC, abstractmethod
import json
import os
from datetime import datetime

import requests

from utils import get_USD_conversion_rate, get_from_and_up_salary


class JobSiteAPI(ABC):
    @abstractmethod
    def get_vacancies(self, filter_word):
        pass


class HeadHunterAPI(JobSiteAPI):

    def get_vacancies(self, filter_word):
        # for page in range(0, 5):
        params = {
            'text': f'NAME:{filter_word}',  # Текст фильтра. В имени должно быть слово "Аналитик"
            'per_page': 50,  # Кол-во вакансий на 1 странице
            'only_with_salary': True,
            'area': 113
        }

        req = requests.get('https://api.hh.ru/vacancies', params)  # Посылаем запрос к API
        jsObj = json.loads(req.content.decode())  # Декодируем его ответ, чтобы Кириллица отображалась корректно
        req.close()
        return jsObj


# print(HeadHunterAPI().get_vacancies('python'))
class SuperJobAPI(JobSiteAPI):
    __api_key = os.getenv('SJ_API_KEY')

    def get_vacancies(self, filter_word):
        headers = {
            'X-Api-App-Id': self.__api_key
        }
        params = {
            'keyword': filter_word,
            'no_agreement': 1,
            'country_id': 1,
            'count': 50
        }
        req = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=headers, params=params)
        jsObj = json.loads(req.content.decode())  # Декодируем его ответ, чтобы Кириллица отображалась корректно
        req.close()
        return jsObj


# print(SuperJobAPI().get_vacancies('python'))

class Vacancy:
    def __init__(self, name: str, employer: str, url: str, area: str,
                 salary_from: int, salary_to: int, currency: str,
                 requirements: str, published_at: str, employment: str):
        self.name = name
        self.employer = employer
        self.url = url
        self.area = area
        self.salary_from = salary_from if salary_from else 0
        self.salary_to = salary_to if salary_to else 0
        self.currency = currency
        self.requirements = requirements
        self.date_string = published_at
        self.employment_type = employment

    @property
    def published_at(self):
        try:
            date = datetime.strptime(self.date_string[:10], '%Y-%m-%d')
            return f'{date.day}-{date.month}-{date.year}'
        except TypeError:
            date = datetime.fromtimestamp(int(self.date_string))
            return f'{date.day}-{date.month}-{date.year}'
    @property
    def approximate_salary(self):
        if self.salary_from and self.salary_to:
            mean_salary = (self.salary_from + self.salary_to) // 2
        else:
            mean_salary = max(self.salary_from, self.salary_to)
        if 'usd' == self.currency.lower():
            return mean_salary * get_USD_conversion_rate()
        else:
            return mean_salary

    def __str__(self):
        response_0 = f'Вакансия на должность: {self.name} в компанию {self.employer} в г. {self.area}\n'

        if self.salary_from and self.salary_to:
            response_1 = f'Зарплата от {self.salary_from} до {self.salary_to} {self.currency}\n'
        elif self.salary_from:
            response_1 = f'Зарплата от {self.salary_from} {self.currency}\n'
        else:
            response_1 = f'Зарплата до {self.salary_to} {self.currency}\n'

        response_2 = f'Требования\Описание:\n{self.requirements}\nТип занятости: {self.employment_type}\n' \
                     f'Вакансия опубликована {self.published_at}\n{self.url}\n{"-" * 80}'
        return response_0 + response_1 + response_2

    def __eq__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary == other.approximate_salary
        return None

    def __ne__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary != other.approximate_salary
        return None

    def __le__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary <= other.approximate_salary
        return None

    def __lt__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary < other.approximate_salary
        return None

    def __ge__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary >= other.approximate_salary
        return None

    def __gt__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary > other.approximate_salary
        return None

    def __sub__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary - other.approximate_salary
        return None

    def __add__(self, other):
        if isinstance(other, Vacancy):
            return self.approximate_salary + other.approximate_salary
        return None


class VacancySaver(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy):
        pass

    @abstractmethod
    def get_vacancies_by_salary(self, salary: str):
        pass


class JSONSaver(VacancySaver):
    def __init__(self):
        self.vacancies = []

    def add_vacancy(self, vacancy):
        if isinstance(vacancy, Vacancy):
            self.vacancies.append(vacancy)
        else:
            print('Error, next time input valid vacancy')

    def delete_vacancy(self, vacancy):
        try:
            self.vacancies.remove(vacancy)
        except ValueError:
            print('Vacancy does not exist')

    def get_vacancies_by_salary(self, salary: str):
        salary_ = get_from_and_up_salary(salary)
        filtered_vacancies = []
        if len(salary_) == 2:
            from_, up_to = salary_
            for element in self.vacancies:
                if from_ < element.approximate_salary() < up_to:
                    filtered_vacancies.append(element)
        else:
            for element in self.vacancies:
                if element.approximate_salary() == salary_:
                    filtered_vacancies.append(element)
        return sorted(filtered_vacancies, key=lambda x: x.approximate_salary, reverse=True)

    def save_to_json(self,file_name):
        string=[(elem.__dict__) for elem in self.vacancies]
        with open(file_name, 'w',encoding='utf-8') as file:
            json.dump(string,file,ensure_ascii=False)