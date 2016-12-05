# coding: UTF-8
from __future__ import unicode_literals

import os, re
import requests
from bs4 import BeautifulSoup


class Scraper:
    '''Класс для скрапинга веб-страниц.
    Выделяет на странице:
        - заголовок по тегу <h1> либо <meta name="title">
        - основной текст по тегам <p> у блоков <div> с указанными классами
    Сохранение страницы в текущую директорию + ./pages/ + url страницы без протокола
    Возможно указание шаблона в папке ./templates/
    Пример ./templates/default.txt
    Использование:
        s = Scrapper()
        s.get('https://someurl.ru/some_page.html')
        s.render_template() # по-умолчанию шаблон 'default'
        s.save()

        s.get('https://someurl.ru/another_page.html')
        s.render_template('sample')
        s.save()
    '''
    def __init__(self):
        self.html = None
        self.bs_obj = None
        self.url = ''
        self.rendered_text = ''

        self.tags_for_remove = ['script', 'noscript', 'style', 'noindex', 'form']
        self.class_attrs_for_remove = ['social', 'reg', 'auth', 'footer', 'banner', 'mobile', 'comment', 'preview', 'inject', 'incut']
        self.class_attrs_for_search = ['content', 'context', 'article', 'text']

        self.string_width = 80
        self.url_tpl = '%url_text% [%url_href%]'
        self.header_tpl = '%header%\r\n\r\n'
        self.p_all_tpl = '%p_all%\r\n'
        self.p_tpl = '%p%\r\n'

        self.header = ''
        self.pub_date_obj = None
        self.p_obj = []
        self.p = []

        self.pages_path = os.path.join(os.getcwd(), 'pages')
        if not os.path.exists(self.pages_path):
            os.makedirs(self.pages_path)
        self.templates_path = os.path.join(os.getcwd(), 'templates')

    def get(self, url=''):
        '''Получение содержимого страницы по URL. Выделение основного содержания страницы.'''
        print('\nЗапрос страницы: {}'.format(url))
        try:
            html = requests.get(url)
        except Exception as e:
            print('Ошибка при запросе страницы: {}'.format(e))
            exit()

        if not html.status_code == 200:
            print('Ошибка при запросе страницы: {}'.format(html.status_code))
            exit()

        self.url = url
        self.html = html

        bs_obj = BeautifulSoup(html.text, 'html.parser')
        self.bs_obj = bs_obj

        self.remove_unnecessary_elements()
        self.get_header()
        self.get_paragraphs()

    def save(self):
        '''Сохранение обработанного содержимого страницы в файл.'''
        self.prepare_path()
        result_path, result_name = os.path.split(self.address_to_save)
        if not os.path.isdir(result_path):
            os.makedirs(result_path)
        print('Путь сохранения: {}'.format(self.address_to_save))

        rendered_text = self.rendered_text.encode('UTF-8')

        with open(self.address_to_save, 'wb') as write_file:
            write_file.write(rendered_text)

        print('Готово.')

    def remove_unnecessary_elements(self):
        """Удаление мешающих для выделения текста элементов"""
        bs_obj = self.bs_obj
        class_attrs_for_remove = '|'.join(self.class_attrs_for_remove)

        if self.tags_for_remove:
            for d in bs_obj.body.findAll(self.tags_for_remove):
                d.extract()

        if class_attrs_for_remove:
            for d in bs_obj.body.findAll(attrs={'class': re.compile(class_attrs_for_remove)}):
                d.extract()

    def get_header(self):
        """Получение заголовка из <h1> либо <meta name="title" content="<Заголовок>">"""
        header = self.bs_obj.body.find('h1')
        if header != None:
            header = header.get_text()
        else:
            header = self.bs_obj.head.find('meta', attrs={'name': 'title'})
            header = header.attrs['content']

        header = self.remove_white_spaces(header)
        self.header = header

    def get_paragraphs(self):
        """Получение объектов <p> тегов"""
        class_attrs_for_search = '|'.join(self.class_attrs_for_search)
        content = self.bs_obj.body.findAll(attrs={"class": re.compile(class_attrs_for_search)})

        p_objects = []
        already_used = []
        for item in content:
            paragraphs = item.findAll('p')
            for p in paragraphs:
                if id(p) in already_used:
                    continue
                if len(p.get_text()) < 30:
                    continue
                p_objects += [p]
                already_used.append(id(p))

        self.p_obj = p_objects

    @staticmethod
    def remove_white_spaces(tmp_str):
        """Удаление пробельных символов"""
        tmp_str = ' '.join(tmp_str.split())
        return tmp_str

    @staticmethod
    def remake_a(tpl, some_parent_tag=None):
        """Изменение текста гиперссылок (изменение только если текст есть)"""
        for a in some_parent_tag.findAll('a'):
            if a.has_attr('href') and a.string :
                tpl = tpl.replace('%url_href%', a.attrs['href'])
                tpl = tpl.replace('%url_text%', a.string)
                a.string.replace_with(tpl)
        return None

    @staticmethod
    def split_lines(words='', max_len=80):
        """Разбивка строк по указанному размеру"""
        max_len -= 1
        words_list = words.split()
        strings_list = ''
        tmp = ''

        for i in range(len(words_list)):
            tmp_current = '{} {}'.format(tmp, words_list[i])
            tmp_current = tmp_current.strip()

            if len(tmp_current) == max_len:
                strings_list += tmp_current + '\r\n'
                tmp = ''
            elif len(tmp_current) > max_len:
                tmp += '\r\n'
                strings_list += tmp
                tmp = words_list[i]
            elif len(tmp_current) < max_len:
                tmp += ' {}'.format(words_list[i])
                tmp = tmp.strip()

        strings_list += tmp
        return strings_list.strip()

    def split_all_lines(self, strings='', max_len=80):
        string_list = strings.splitlines()
        new_string_list = []
        for i in range(len(string_list)):
            new_string_list.append(self.split_lines(string_list[i], max_len))

        return '\r\n'.join(new_string_list)

    def prepare_path(self):
        """Получение конечного пути для сохранения страницы"""
        url = self.url
        sub_url = re.findall(r'.*://(.*)', url)[0]

        sub_url = os.path.splitext(sub_url)[0]
        if sub_url.endswith('/'):
            sub_url = sub_url[:-2]

        address_to_save = os.path.abspath(self.pages_path + '/'  + sub_url + '.txt')
        self.address_to_save = address_to_save

    def read_config_and_template(self, tplname='default'):
        """Чтение файла-шаблона с настройками"""
        template_file = self.templates_path + '/' + tplname + '.txt'
        if not os.path.exists(template_file):
            print('Ошибка: шаблон {} не найден'.format(tplname))
            return

        with open(template_file, 'rb') as tpl_file:
            tpl = tpl_file.read()
            tpl = tpl.decode('UTF-8')

            t = re.search(r'\[tags_for_remove\]=(.*)\r\n', tpl)
            if t:
                if t.groups():
                    self.tags_for_remove = t.group(1).split()
                else:
                    self.tags_for_remove = []

            t = re.search(r'\[class_attrs_for_remove\]=(.*)\r\n', tpl)
            if t:
                if t.groups():
                    self.class_attrs_for_remove = t.group(1).split()
                else:
                    self.class_attrs_for_remove = []

            t = re.search(r'\[class_attrs_for_search\]=(.*)\r\n', tpl)
            if t:
                if t.groups():
                    self.class_attrs_for_search = t.group(1).split()
                else:
                    self.class_attrs_for_search = []

            t = re.findall(r'\[string_width\]=(\d+)', tpl)
            if t:
                self.string_width =  int(t[0])

            t = re.findall(r'\[url\]=(.*%url_text%.*%url_href%.*)\r\n', tpl)
            if t:
                self.url_tpl = t[0]

            t = re.findall(r'%header_begin%(.*%header%.*)%header_end%', tpl, flags=re.M | re.S)
            if t:
                self.header_tpl = t[0]

            t = re.findall(r'%p_all_begin%(.*%p_all%.*)%p_all_end%', tpl, flags=re.M | re.S)
            if t:
                self.p_all_tpl = t[0]

            t = re.findall(r'%p_begin%(.*%p%.*)%p_end%', tpl, flags=re.M | re.S)
            if t:
                self.p_tpl = t[0]

    def render_template(self, tplname=''):
        """Преобразование промежуточных данных в текст для сохранения"""
        if tplname:
            print('Шаблон: {}'.format(tplname))
            self.read_config_and_template(tplname)
        else:
            self.read_config_and_template()
            print('Шаблон по-умолчанию')

        string_width = self.string_width
        url_tpl = self.url_tpl
        header_tpl = self.header_tpl
        p_all_tpl = self.p_all_tpl
        p_tpl = self.p_tpl

        rendered_text = header_tpl.replace('%header%', self.header)

        paragraphs = ''
        for p in self.p_obj:
            self.remake_a(url_tpl, p)
            p_string = self.remove_white_spaces(p.get_text())
            paragraphs += p_tpl.replace('%p%', p_string)

        rendered_text += p_all_tpl.replace('%p_all%', paragraphs)
        rendered_text = self.split_all_lines(rendered_text, string_width)

        self.rendered_text = rendered_text
