_do_GET()_ - парсит строку запроса и, при помощи регулярных выражений, вызывает соответствующий метод.

_send_info_by_id(id)_ - вызывется если были переданы цифры в URL. Возвращает json с информацией о городе.

_send_info_by_page(page, count)_ - вызывается если была передана пара цифр, разделенных символом подчеркивания '_'. Возвращает json с информацией о городах.

_send_info_by_names(first, second)_ - вызывется если была передана пара строк, разделенных символом подчеркивания '_'. Возвращает json с информацией о городах, о том какой из городов севернее("northern") и о том какая разница в часовых поясах между этими городами(timeDiff).

_get_info_by_name(name)_ - возвращает информацию о найденом городе или None.

_send_prompt(name)_ - вызывется если полученное имя не было найдено в базе данных и возвращает json с возможными подсказками.

_lev(s1, s2)_ - возвращает расстояние Ливенштейна.

_get_with_headers(info)_ - возвращает словарь, для переданной строки.