import requests

from lxml import html
print("henlo")

url = 'https://fr.wikisource.org/w/index.php?title=Maximes&printable=yes'
res = requests.get(url)
with open('maximes.html', 'wb') as out:
    out.write(res.text.encode('utf-8'))
