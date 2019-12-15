import csv
import re

src = './outfit_products.csv'
category = {}

with open(src, 'r', encoding='utf-8') as doc:
    rows = csv.reader(doc, delimiter=',')

    for row in rows:
        categories = row[1].replace('"', '').replace(',', ' ').strip()
        categories = categories.split(' ')
        for c in categories:
            if c not in category.keys():
                c = re.sub('[-\'"\[\]+\./\(\):;|#\\\\]', '', c)
                c.strip()
                category[c] = 0
            category[c] += 1

categories = []
for key, value in category.items():
    print(key, ' ', value)
    categories.append((key, value))
categories.sort(key=lambda x: x[1], reverse=True)
print('length: ', len(category.items()))

with open('categories.csv', 'w', newline='', encoding='utf-8') as doc:
    Writer = csv.writer(doc)
    for category in categories:
        Writer.writerow(category)