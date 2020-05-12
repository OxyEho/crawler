# Crawler

Ищет ссылки по заданному запросу и скачивает их содержимое

Программа принимает на вход ссылку, с которой начинается поиск и запрос

## Установка

    git clone https://github.com/OxyEho/crawler

    pip install -r requirements.txt

## Запуск 

    python main.py some_start_url some_request -d 10

    Опция -d задает максимальное количество просмотренных ссылок
    
    Опция --wildcard задает домены, которые можно посещать 
    
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