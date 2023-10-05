from bs4 import BeautifulSoup
import requests


def get_USD_conversion_rate():
    exchange_url = 'https://quote.ru/ticker/59111'
    exchange_page = requests.get(exchange_url)
    soup = BeautifulSoup(exchange_page.text, "html.parser")
    rub = soup.find('div', class_="MuiGrid-root MuiGrid-item quote-style-1jaw3oe").text.split()[1].replace(',', '.')
    return float(rub)


def get_from_and_up_salary(salary):
    string_list = salary[: -4].split('-:')
    currency = salary[-4:]
    if len(string_list) == 2:
        from_ = int(string_list[0].replace(' ', ''))
        up_to = int(string_list[1].replace(' ', ''))
        if 'usd' in currency.lower():
            from_ *= get_USD_conversion_rate()
            up_to *= get_USD_conversion_rate()
        return from_, up_to
    else:
        mean_salary = int(string_list[0].replace(' ', ''))
        if 'usd' in currency.lower():
            mean_salary *= get_USD_conversion_rate()
        return [mean_salary]


def filter_vacancies(vacancies, filter_words: list):
    filtered_vacancies = set()
    for vacancy in vacancies:
        for word in filter_words:
            for value in vacancy.__dict__.values():
                if str(word).casefold() in str(value).casefold():
                    filtered_vacancies.add(vacancy)
                    break
    #sorted_vacancies = sorted(list(filtered_vacancies), key=lambda x: x.approximate_salary, reverse=True)
    return filtered_vacancies


def print_top_vacancies(vacancies, top_n: int = 10):
    index = min(top_n, len(vacancies))
    for vacancy in vacancies[:index]:
        print(vacancy)

def sort_vacancies(vacancies):
    return sorted(vacancies, key=lambda x: x.approximate_salary, reverse=True)

