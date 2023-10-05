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
        params = {
            'text': f'NAME:{filter_word}',
            'per_page': 50,
            'only_with_salary': True,
            'area': 113
        }

        req = requests.get('https://api.hh.ru/vacancies', params)
        jsObj = json.loads(req.content.decode())
        req.close()
        return jsObj


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
        jsObj = json.loads(req.content.decode())
        req.close()
        return jsObj


class Vacancy:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

    @property
    def published_at(self):
        try:
            date = datetime.strptime(self.published[:10], '%Y-%m-%d')
            return f'{date.day}-{date.month}-{date.year}'
        except ValueError:
            return self.published
        except TypeError:
            date = datetime.fromtimestamp(int(self.published))
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


class Saver:
    def __init__(self):
        self.vacancies = []

    def add_vacancy(self, vacancy):
        if isinstance(vacancy, Vacancy):
            self.vacancies.append(vacancy)
        else:
            print('Error, next time input valid vacancy')

    def add_hh_vacancies(self, search_query):
        vacancies_hh = HeadHunterAPI().get_vacancies(search_query)
        for vacancy_hh in vacancies_hh['items']:
            try:
                dic = {
                    'name': vacancy_hh['name'],
                    'employer': vacancy_hh['employer']['name'],
                    'url': vacancy_hh['alternate_url'],
                    'area': vacancy_hh['area']['name'],
                    'salary_from': vacancy_hh['salary']['from'] if vacancy_hh['salary']['from'] else 0,
                    'salary_to': vacancy_hh['salary']['to'] if vacancy_hh['salary']['to'] else 0,
                    'currency': vacancy_hh['salary']['currency'],
                    'requirements': vacancy_hh['snippet']['requirement'],
                    'published': vacancy_hh['published_at'],
                    'employment_type': vacancy_hh['employment']['name']
                }
            except KeyError:
                continue
            vacancy = Vacancy(dic)
            self.add_vacancy(vacancy)

    def add_sj_vacancies(self, search_query):
        vacancies_sj = SuperJobAPI().get_vacancies(search_query)
        for vacancy_sj in vacancies_sj['objects']:
            try:
                dic = {
                    'name': vacancy_sj['profession'],
                    'employer': vacancy_sj['client']['title'],
                    'url': vacancy_sj['link'],
                    'area': vacancy_sj['town']['title'],
                    'salary_from': vacancy_sj['payment_from'] if vacancy_sj['payment_from'] else 0,
                    'salary_to': vacancy_sj['payment_to'] if vacancy_sj['payment_to'] else 0,
                    'currency': vacancy_sj['currency'],
                    'requirements': vacancy_sj['candidat'],
                    'published': vacancy_sj['date_published'],
                    'employment_type': vacancy_sj['type_of_work']['title']
                }
            except KeyError:
                continue
            vacancy = Vacancy(dic)
            self.add_vacancy(vacancy)

    def delete_vacancy(self, vacancy):
        try:
            self.vacancies.remove(vacancy)
        except ValueError:
            print('Vacancy does not exist')

    def get_vacancies_by_salary(self, salary: str):
        try:
            salary_ = get_from_and_up_salary(salary)
        except ValueError:
            raise ValueError(
                'Введите запрос в одном из форматов "50 000- 100 000 руб." "1000-2000 USD"  "100_000 руб."')
        filtered_vacancies = []
        if len(salary_) == 2:
            from_, up_to = salary_
            for vacancy in self.vacancies:
                if from_ < vacancy.approximate_salary < up_to:
                    filtered_vacancies.append(vacancy)
        else:
            for vacancy in self.vacancies:
                if vacancy.approximate_salary == salary_[0]:
                    filtered_vacancies.append(vacancy)
        return filtered_vacancies


class JSONSaver(Saver):
    def __init__(self):
        super().__init__()

    def save_to_json(self, file_name):
        string = [elem.__dict__ for elem in self.vacancies]
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(string, file, ensure_ascii=False)

    def get_from_json(self, file_name):
        self.vacancies.clear()
        with open(file_name, 'r', encoding='utf-8') as file:
            vacancies_json = json.load(file)
            for dict_json in vacancies_json:
                vacancy = Vacancy(dict_json)
                self.add_vacancy(vacancy)
        return
