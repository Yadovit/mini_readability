# coding: UTF-8
from __future__ import unicode_literals

import sys, os, re
from minread_mod import Scraper

if len(sys.argv) < 2:
    print('Пример использования:\n{} https://someurl.ru/some_page.html mytemplate\n'.format(os.path.split(sys.argv[0])[1]))
    exit()

template_name = ''
url = sys.argv[1]

if len(sys.argv) == 3:
    template_name = sys.argv[2]

s = Scraper()
s.get(url)
s.render_template(template_name)
s.save()