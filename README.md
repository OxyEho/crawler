# Crawler

Ищет ссылки по заданному запросу и скачивает их содержимое

Программа принимает на вход ссылку, с которой начинается поиск и запрос

## Установка

    git clone https://github.com/OxyEho/crawler

    pip install -r requirements.txt

## Запуск 

    python main.py some_start_url some_request -d 10 --wildcard *.wikipedia.org -f result

    Опция -d задает максимальное количество просмотренных ссылок
    
    Опция -f указывает директорию, в которую будут скачаны найденные страницы
    
    Опция -w указывает будут ли скачены найденные страницы
    
    Опция --wildcard задает домены, которые можно посещать 
    
    Опция -g указывает будет ли показан граф поиска страниц
    
    Синтаксис 
    
        --wildcard *.wikipedia.org
       
    При таком задании параметра для посещения будут доступны www.wikipedia.org, en.wikipedia.org, ru.wikipedia.org


#### Пример работы crawler

    python main.py https://docs.scala-lang.org/ru/tour/tour-of-scala.html scala -d 5 --wildcard *.scala-lang.org

    https://docs.scala-lang.org/ru/tour/tour-of-scala.html
    https://docs.scala-lang.org//ru
    https://www.scala-lang.org/community/
    https://docs.scala-lang.org//
    https://www.scala-lang.org/contribute/
    Program is completed



## Запрос

Запрос может состоять более чем из одного слова