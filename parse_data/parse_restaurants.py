import requests
from bs4 import BeautifulSoup
import re  
import mysql.connector
import xlwt

HOST = 'https://restoran.kz'
URL = 'restaurant'

HEADERS = {
    'accept': 'image/webp,*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}

#получение html страницы
def get_Html(url):
    response = requests.get(url, headers=HEADERS)
    return response.text

#функция для парсинга html страницы
def parser(page):
    html = get_Html(HOST + '/' + URL + '?page=' + str(page))
    bs = BeautifulSoup(html, 'html.parser')
    print(page)

    tegs_h3 = bs.findAll('h3', class_='h2 place-list-card__title')
    divs = bs.findAll('div', class_='list-unstyled mb-4')

    pattern = re.compile(r'<use xlink:href=\".+?\"></use></svg>(.+?)</li>')

    details = []
    for index,el in enumerate(divs):
        subject = el.findAll('li', 'd-flex mr-5 mb-3')
        details.append([])
        for match in subject:
            details[index].append(re.findall('\<use xlink:href=\".+?\"\>\<\/use\>\<\/svg\>(.+?)\<\/li\>', str(match)))

    result = []
    for index,item in enumerate(tegs_h3):
        result.append({
            'name': item.text,
            'link': HOST + item.find('a', class_='link-inherit-color').get('href'),
            'cuisines': details[index][0][0] if len(details[index]) > 0 else '',
            'price': details[index][1][0] if len(details[index]) > 1 else '',
            'options': details[index][2][0] if len(details[index]) > 2 else '',
        })

    return result

#функция для получение максимальной страницы
def get_max_page(page):
    html = get_Html(HOST + '/' +  URL + '?page='+str(page))
    
    bs = BeautifulSoup(html, 'html.parser')
    pagination = bs.findAll('ul',class_ = 'pagination')
    
    pattern = re.compile(r'\d+')
    matches = pattern.findall(str(pagination))

    max_page = max(list(map(int,matches)))

    if page != max_page:
        return get_max_page(max_page)
    else:
        return max_page

#преобразование из словаря в список
def dict_to_list(arg):
    arr = list()
    for i in arg:
        arr.append(arg[i])
    return arr

#получение максимальной страницы
max_page_res = get_max_page(1)


#добавление всех ресторанов из всех страниц
result = []
for page in range(1, max_page_res+1):
    result.extend(parser(page))

#запись в excel
book = xlwt.Workbook()
sheet1 = book.add_sheet("Sheet1")
cols = ["A", "B", "C", "D", "E"]
for i in range(len(result)):
    arr = dict_to_list(result[i])
    row = sheet1.row(i)
    for index, col in enumerate(cols):
        value = arr[index]
        row.write(index, value)
book.save("restaurants.xls")