from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from csv import reader
from re import fullmatch
from json import dumps


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = parse.urlparse(self.path)

        self.send_response(200)
        self.send_header('content-type', 'text/html; charset=utf-8')
        self.end_headers()

        if fullmatch(r'/\d{6,8}', request.path):
            self.send_info_by_id(request.path[1:])
        elif fullmatch(r'/\d+_\d+', request.path):
            page, count = [int(i) for i in request.path[1:].split('_')]
            self.send_info_by_page(page, count)
        elif fullmatch(r'/[-\w ]+_[-\w ]+', parse.unquote(request.path)):
            first, second = parse.unquote(request.path)[1:].split('_')
            self.send_info_by_names(first, second)
        else:
            self.wfile.write("Wrong command".encode())

    @staticmethod
    def get_with_headers(info):
        headers = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class",
                   "feature code", "country code", "cc2", "admin1 code", "admin2 code", "admin3 code", "admin4 code",
                   "population", "elevation", "dem", "timezone", "modification date"]
        map = {}
        for i in range(len(headers)):
            map[headers[i]] = info[i]
        return map

    def send_info_by_id(self, geonameid):
        for city in self.server.storage:
            if city[0] == geonameid:
                self.wfile.write(dumps(myHandler.get_with_headers(city), ensure_ascii=False).encode())
                return

        self.wfile.write(f"No city with geonameid - {geonameid}".encode())

    def send_info_by_page(self, page, count):
        page -= 1

        res = []
        for i, city in enumerate(self.server.storage):
            if i == page * self.server.pageSize + count:
                break
            if i >= page * self.server.pageSize:
                res.append(myHandler.get_with_headers(city))
        self.wfile.write(dumps(res, ensure_ascii=False).encode())

    def send_info_by_names(self, first, second):
        firstRes = self.get_info_by_name(first)
        secondRes = self.get_info_by_name(second)

        # Проверка полученны ли города, если не получены - то вывести подсказу
        if firstRes is None:
            self.send_prompt(first)
            return
        if secondRes is None:
            self.send_prompt(second)
            return

        resp = {}
        resp["first"] = myHandler.get_with_headers(firstRes)
        resp["second"] = myHandler.get_with_headers(secondRes)

        # Вывод доп инфы
        if float(firstRes[4]) > float(secondRes[4]):
            resp["northern"] = first
        else:
            resp["northern"] = second

        resp["timeDiff"] = float(self.server.timeZones[secondRes[17]]) - float(self.server.timeZones[firstRes[17]])
        self.wfile.write(dumps(resp, ensure_ascii=False).encode())

    def get_info_by_name(self, name):
        find = None

        for city in self.server.storage:
            if name in city[3].split(','):
                if find is None:
                    find = city
                elif int(city[14]) > int(find[14]):
                    find = city

        return find

    @staticmethod
    def lev(s1, s2):
        d = {}
        lenstr1 = len(s1)
        lenstr2 = len(s2)
        for i in range(-1, lenstr1 + 1):
            d[(i, -1)] = i + 1
        for j in range(-1, lenstr2 + 1):
            d[(-1, j)] = j + 1

        for i in range(lenstr1):
            for j in range(lenstr2):
                if s1[i] == s2[j]:
                    cost = 0
                else:
                    cost = 1
                d[(i, j)] = min(
                    d[(i - 1, j)] + 1,  # deletion
                    d[(i, j - 1)] + 1,  # insertion
                    d[(i - 1, j - 1)] + cost,  # substitution
                )
                if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                    d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + 1)  # transposition

        return d[lenstr1 - 1, lenstr2 - 1]

    def send_prompt(self, name):
        prompt = set()
        kirill = ('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
        k = 3
        for city_info in self.server.storage:
            for city_name in city_info[3].split(','):
                if city_name != '' and \
                        city_name[0].lower() in kirill and \
                        abs(len(name) - len(city_name)) <= k and \
                        myHandler.lev(city_name, name) <= len(name) // k:
                    prompt.add(city_name)
                    break
            if len(prompt) == 5:
                break
        if len(prompt) == 0:
            self.wfile.write(f"No prompt for {name}".encode())
            return
        print(prompt)
        self.wfile.write(dumps({"prompt": list(prompt)}, ensure_ascii=False).encode())


class myServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, DataBase="RU.txt", pageSize=50):
        super().__init__(server_address, RequestHandlerClass)

        self.timeZones = {'Asia/Anadyr': '12.0', 'Asia/Aqtobe': '5.0', 'Asia/Ashgabat': '5.0', 'Asia/Baku': '4.0',
                     'Asia/Barnaul': '7.0', 'Asia/Chita': '9.0', 'Asia/Hovd': '7.0', 'Asia/Irkutsk': '8.0',
                     'Asia/Kamchatka': '12.0', 'Asia/Khandyga': '9.0', 'Asia/Krasnoyarsk': '7.0',
                     'Asia/Magadan': '11.0', 'Asia/Novokuznetsk': '7.0', 'Asia/Novosibirsk': '7.0', 'Asia/Omsk': '6.0',
                     'Asia/Qyzylorda': '5.0', 'Asia/Sakhalin': '11.0', 'Asia/Shanghai': '8.0',
                     'Asia/Srednekolymsk': '11.0', 'Asia/Tashkent': '5.0', 'Asia/Tbilisi': '4.0', 'Asia/Tokyo': '9.0',
                     'Asia/Tomsk': '7.0', 'Asia/Ulaanbaatar': '8.0', 'Asia/Ust-Nera': '10.0',
                     'Asia/Vladivostok': '10.0', 'Asia/Yakutsk': '9.0', 'Asia/Yekaterinburg': '5.0',
                     'Europe/Astrakhan': '4.0', 'Europe/Helsinki': '2.0', 'Europe/Kaliningrad': '2.0',
                     'Europe/Kiev': '2.0', 'Europe/Kirov': '3.0', 'Europe/Minsk': '3.0', 'Europe/Monaco': '1.0',
                     'Europe/Moscow': '3.0', 'Europe/Oslo': '1.0', 'Europe/Paris': '1.0', 'Europe/Riga': '2.0',
                     'Europe/Samara': '4.0', 'Europe/Saratov': '4.0', 'Europe/Simferopol': '3.0',
                     'Europe/Ulyanovsk': '4.0', 'Europe/Vilnius': '2.0', 'Europe/Volgograd': '3.0',
                     'Europe/Warsaw': '1.0', 'Europe/Zaporozhye': '2.0'}
        self.pageSize = pageSize

        self.storage = []
        with open(DataBase, encoding='utf-8') as f:
            file = reader(f, delimiter='\t')
            for city in file:
                self.storage.append(city)


def main():
    addr = ('127.0.0.1', 8000)
    server = myServer(addr, myHandler, "RU.txt", 50)
    server.serve_forever()


if __name__ == '__main__':
    main()
