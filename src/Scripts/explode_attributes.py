import csv

import pandas
import numpy as np


data = pandas.read_csv('./data.csv', encoding='utf-8')

for i in range(0, len(data)):
    categories = data.loc[i, 'categories']
    if pandas.isna(categories): continue
    print(i)
    categories = categories.split(',')

    j = 0
    for category in categories:
        category = category.strip()
        data.loc[i, 'category{}'.format(j)] = category
        j += 1

data.to_csv('./data.csv', encoding='utf-8', index=False)
