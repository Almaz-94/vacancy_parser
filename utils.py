from bs4 import BeautifulSoup
import requests
def get_USD_conversion_rate():
    exchange_url = 'https://quote.ru/ticker/59111'
    exchange_page = requests.get(exchange_url)
    soup = BeautifulSoup(exchange_page.text, "html.parser")
    rub = soup.find('div', class_="MuiGrid-root MuiGrid-item quote-style-1jaw3oe").text.split()[1].replace(',','.')
    return float(rub)

def get_from_and_up_salary(salary):
    string_list = salary[: -4].split('-')
    currency = salary[-4:]
    if len(string_list) == 2:
        from_ = int(string_list[0].replace(' ', '_'))
        up_to = int(string_list[1].replace(' ', '_'))
        if 'usd' in currency.lower():
            from_ *= get_USD_conversion_rate()
            up_to *= get_USD_conversion_rate()
        return from_, up_to
    else:
        mean_salary = int(string_list[0].replace(' ', '_'))
        if 'usd' in currency.lower():
            mean_salary *= get_USD_conversion_rate()
        return mean_salary

