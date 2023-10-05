from classes import JSONSaver
from utils import filter_vacancies, print_top_vacancies, sort_vacancies


def user_interaction():
    platform = input('Выберите сайт для поиска:\nHeadHunter\nSuperJob\nBoth\n').lower()
    if platform not in ['headhunter', 'superjob', 'both', 'hh', 'sj']:
        raise ValueError('Некорректный запрос- ожидается один из предложенных вариантов, перезапустите скрипт')

    search_query = input("Введите поисковый запрос:\n")
    try:
        top_n = int(input("Введите количество вакансий для вывода в топ N:\n"))
    except ValueError:
        raise ValueError('Некорректный запрос- ожидается число. Перезапустите скрипт')
    filter_words = input("Введите ключевые слова для фильтрации вакансий:\n").split()

    json_saver = JSONSaver()
    if platform in ['headhunter', 'hh', 'both']:
        json_saver.add_hh_vacancies(search_query)

    if platform in ['superjob', 'sj', 'both']:
        json_saver.add_sj_vacancies(search_query)

    if filter_words:
        filtered_vacancies = filter_vacancies(json_saver.vacancies, filter_words)
        sorted_vacancies = sort_vacancies(filtered_vacancies)
        print_top_vacancies(sorted_vacancies, top_n)
        if not filtered_vacancies:
            print("Нет вакансий, соответствующих заданным критериям.")
    else:
        sorted_vacancies = sort_vacancies(json_saver.vacancies)
        if not sorted_vacancies:
            print("Нет вакансий, соответствующих заданным критериям.")
        print_top_vacancies(sorted_vacancies, top_n)

    filter_by_salary = input("Хотите поискать вакансии по зарплате? (Да\Нет\Yes\\No)\n").lower()
    if filter_by_salary in ['да', 'yes']:
        salary = input("Введите интервал желаемой зарплаты и валюту \n")  # 50 000- 100 000 руб./1000 USD
        vac_by_salary = json_saver.get_vacancies_by_salary(salary)
        sorted_vacancies = sort_vacancies(vac_by_salary)
        if not sorted_vacancies:
            print("Нет вакансий, соответствующих заданным критериям.")
        print_top_vacancies(sorted_vacancies, top_n)

    json_saver.save_to_json('Vacancies.json')
    json_saver2 = JSONSaver()
    json_saver2.get_from_json('Vacancies.json')


if __name__ == '__main__':
    user_interaction()
