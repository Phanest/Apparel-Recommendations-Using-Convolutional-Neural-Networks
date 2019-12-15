import csv
import pandas

def tidyDuplicates(row):
    link = row['href']
    if pandas.isna(link):
        return row

    if link in dict.keys():
        id = dict[link]
        row['id'] = id
    else:
        id = row['id']
        dict[link] = id
    return row

dict = {}
data = pandas.read_csv('./data.csv', encoding='utf-8')
data = data.apply(tidyDuplicates, axis=1)

data.to_csv('./data.csv', encoding='utf-8', index=False)
with open('duplicates.csv', 'w', newline='', encoding='utf-8') as doc:
    Writer = csv.writer(doc)
    for key, value in dict.items():
        Writer.writerow([key, value])

