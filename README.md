# Mini readability

### Суть проекта
Позволяет скрапить сайты.
Сохраняет результат в txt-файл по пути, получаемого преобразованием из url.

### Исполняемые модули:
* minread_shell.py - используется для запуска 
* minread_mod.py - модуль для класса Scraper 

### Зависимости.
* [requests](https://github.com/kennethreitz/requests)
* [beautifulsoup4](https://launchpad.net/beautifulsoup)

### Пример вызова в коммандной строке: 
`minread_shell.py https://someurl.ru/some_page.html`

### Пример обращения к классу: 
```python
  s = Scraper()
  s.get(url)
  s.render_template(template_name)
  s.save()
```


### Подробнее: 
В данный момент умеет следующее: 
* выделять заголовок из `<h1>` и `<meta name="title" content="">`
* выделять текст из `<p>`
* указывать теги и значения для атрибута `<div class="">`, которые можно удалить перед поиском
* значения для атрибута `<div class="">` тегов, в потомках которых будет идти поиск
* изменять текст гиперссылок для наглядности в txt-варианте
* использовать шаблон для форматирования текста

### Шаблоны.
txt-файлы, в которых можно указывать настройки и правила форматирования.
Хранятся в директории `./templates/`
При указании в коммандной строке указывается без расширения.

* Теги для удаления:
 + `[tags_for_remove]=script noscript style noindex form`
* Атрибуты тегов для удаления:
 + `[class_attrs_for_remove]=social reg auth footer banner mobile comment preview inject incut`
* Атрибуты тегов, в дочерних элементах которых будет поиск текста.
 + `[class_attrs_for_search]=content context article text`
* Максимальный размер строки. При превышение будет разбивка на строки.
 + `[string_width]=80`
* Шаблон замена текста гиперссылки. После знака = и до конца строки можно указать различный текст, в который будет обёрнута ссылка.
 + `[url]=%url_text% [%url_href%]`
 + Пример: для `<a href="https://ya.ru/">Яндекс</a>` с шаблоном `'Перейти -> %url_text% [%url_href%]'` будет результат:
 + `<a href="https://ya.ru/">Перейти -> Яндекс [https://ya.ru/]</a>`
* Шаблон заголовка. Разрешены переносы строк.
 + `%header_begin% *** %header% *** %header_end%`
 + Всё между тегами `%header_begin%` и `%header_end%` попадёт в шаблон. `%header%` заменится на заголовок.
* Шаблон всего текста статьи. Разрешены переносы строк.
 + `%p_all_begin%%p_all%%p_all_end%`
 + Всё между псевдотегами `%p_all_begin%` и `%p_all_end%` попадёт в шаблон. `%p_all%` заменится весь текст статьи.
* Шаблон отдельного абзаца. Разрешены переносы строк.
 + `%p_begin% %p% %p_end%`
 * Всё между псевдотегами `%p_begin%` и `%p_end%` попадёт в шаблон. `%p%` заменится на текст абзаца.


### Сохранение
Сохранение происходит в UTF-8.
Путь для сохранения вычисляется по URL страницы следующим образом:
 - отбрасывается обозначение протокола `*://`
 - к оставшемуся пути вначале добавляется `./pages/`
 - проверяется наличие директорий, при небходимости создаюся недостающие вложенные директории
 - сохранение файла
 
