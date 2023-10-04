from classes import Vacancy, HeadHunterAPI, SuperJobAPI, JSONSaver
def user_interaction():
    platform = 'both'
    search_query = 'python'
    top_n = 10
    # platform = input('Выберите сайт для поиска:\nHeadHunter\nSuperJob\nBoth\n')
    # search_query = input("Введите поисковый запрос: ")
    # top_n = int(input("Введите количество вакансий для вывода в топ N: "))
    # filter_words = input("Введите ключевые слова для фильтрации вакансий: ").split()
    json_saver = JSONSaver()
    if platform.lower() in ['headhunter', 'both']:
        vacancies_hh = HeadHunterAPI().get_vacancies(search_query)
        for vacancy_hh in vacancies_hh['items']:
            name = vacancy_hh['name']
            employer = vacancy_hh['employer']['name']
            url = vacancy_hh['alternate_url']
            area = vacancy_hh['area']['name']
            salary_from = vacancy_hh['salary']['from']
            salary_to = vacancy_hh['salary']['to']
            currency = vacancy_hh['salary']['currency']
            requirements = vacancy_hh['snippet']['requirement']
            published = vacancy_hh['published_at']
            employment = vacancy_hh['employment']['name']

            vacancy = Vacancy(name,employer,url,area,salary_from,salary_to,currency,requirements,published,employment)

            json_saver.add_vacancy(vacancy=vacancy)
    if platform.lower() in ['superjob', 'both']:
        vacancies_sj = SuperJobAPI().get_vacancies(search_query)
        for vacancy_sj in vacancies_sj['objects']:
            name = vacancy_sj['profession']
            employer = vacancy_sj['client']['title']
            url = vacancy_sj['link']
            area = vacancy_sj['town']['title']
            salary_from = vacancy_sj['payment_from']
            salary_to = vacancy_sj['payment_to']
            currency = vacancy_sj['currency']
            requirements = vacancy_sj['candidat']
            published = vacancy_sj['date_published']
            employment = vacancy_sj['type_of_work']['title']

            vacancy = Vacancy(name, employer, url, area, salary_from,salary_to,currency, requirements, published, employment)

            json_saver.add_vacancy(vacancy=vacancy)
    json_saver.vacancies.sort(key=lambda x: x.approximate_salary, reverse = True)
    for i in range(top_n):
        print(json_saver.vacancies[i])
if __name__ == '__main__':
    user_interaction()
