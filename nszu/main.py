import re
from time import sleep
import pymysql.cursors
import schedule
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By


def db_option():
    global connection  # Вообще нежелательно, но в данном случае пришлось установить connection глобально
    try:  # Подключение к бд
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123ADMINpassword777',
            database='my_db',
            cursorclass=pymysql.cursors.DictCursor,
        )
        print('Connect successfully')
    except Exception as ex:
        print('Failed to connect')
        print(ex)

    try:  # Изначально создавал таблицу прямо здесь, но после создал её через django и просто подключаюсь к той бд
        with connection.cursor() as cursor:
            create_table_query = "CREATE TABLE IF NOT EXISTS `worker_news` (news_id INT primary key," \
                                 " header TEXT," \
                                 " link TEXT," \
                                 " img TEXT," \
                                 " text LONGTEXT)"
            cursor.execute(create_table_query)
        print('All right!')
    except Exception as ex:
        print('Table problem')
        print(ex)

    main()

# Непосредственно сам парсер
def main():
    options = webdriver.ChromeOptions()
    '''
    Так как на ресурсе, откуда парсим данные установлена защита Cloudflare от DDoS, что бы не тратить время на 
    изучение как к вебдрайверу selenium добавить список разных user agent и прочее, мною было принято решение 
    использовать эту библиотеку. Единственный её минус, для того, чтобы все работало, ему необходимо открывать явно 
    окно браузера и опция add_argument('headless') не помогает. Просто дальше не редиректит.
    '''
    driver = uc.Chrome(options=options)
    '''
    Захожу на первую страницу новостей, жду пока пропустит меня и после беру значение последней ссылки, для того, 
    что бы пройтись по всем страницам.
    '''
    driver.get('https://nszu.gov.ua/novini?page=1')
    driver.implicitly_wait(15)
    page = int(driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[3]/ul/li[12]/a").text)
    print(page)

    counter = 0  # Счетчик попыток найти новую новость, которой ещё нет у нас в БД
    for page in range(1, page+1):  # В этом цикле проходим по страницам и внутри каждой страницы берем
        # все ссылки на новости
        sleep(1)  # Сон я сделал потому, что меня уже блокировали по IP, что бы парсер был больше похож на пользователя
        driver.get(f'https://nszu.gov.ua/novini?page={page}')
        elems = driver.find_elements(By.CSS_SELECTOR, ".news-block-title-m [href]")
        links = [elem.get_attribute('href') for elem in elems]
        # В списке выше ссылки на все новости, на текущей странице
        sleep(1)

        for link in links:  # Проходимся по каждой новости и парсим изнутри данные
            news_id = int(re.findall(r"\d+$", link)[0])  # Беру айдишник новости, что бы положить в бд,
            # дальше с помощью него я смогу проверять, есть ли такие уже данные(новости) в бд
            sleep(1)
            driver.get(link)
            header = driver.find_element(By.XPATH, "/html/body/div/h1")
            header_txt = header.text
            try:
                news_img = driver.find_element(By.XPATH, "//img[contains(@class, 'fr-draggable')]").get_attribute('src')
            except:
                news_img = None  # В некоторых новостях нет внутри картинок, страница сама по себе будто сломана

            '''Основной текст по какой то из причин лежит у них в 3х разных путях. В целом можно было так же этот 
            код заменить циклом, где с каждым проходом будет инкрементироваться цифра внутри p[]'''
            text = driver.find_element(By.XPATH,
                                       "/html/body/div/div[1]/div[1]/div/div[2]/div/div/article/div/p[1]").text
            if not text:
                text = driver.find_element(By.XPATH,
                                           "/html/body/div/div[1]/div[1]/div/div[2]/div/div/article/div/p[2]").text
            if not text:
                text = driver.find_element(By.XPATH,
                                           "/html/body/div/div[1]/div[1]/div/div[2]/div/div/article/div/p[3]").text
            # Проверяю есть ли такой айдшник новости в БД, если есть - вывожу новость, если нет - добавляю в бд.
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM worker_news WHERE news_id={news_id}")
                    row = cursor.fetchone()
                    print(row)
                    if not row:
                        insert_query = \
                            "INSERT INTO `worker_news` (news_id, header, link, img, text) VALUES (%s, %s, %s, %s, %s);"
                        record = (news_id, header_txt, link, news_img, text)
                        cursor.execute(insert_query, record)
                        connection.commit()
                    # Счетчик попыток: на странице 9 новостей, даю 9 попыток найти новые статьи на текущей
                    # странице - если не находит, то программа завершается
                    if row:
                        counter += 1
                    if counter >= 9:
                        return
            except Exception as ex:
                print('Problem in checking/writing data')
                print(ex)
    driver.quit()
    connection.close()


# Метод, в которой выбираем интервал запуска программы и в бесконечном цикле запускаем постоянный процесс
def scheduler():
    schedule.every().day.at("00:00").do(db_option)

    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    scheduler()











