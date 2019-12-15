import csv
import re
import pandas

category = (
'jeans',
'hose',
'gürtel',
'jacke',
'chino',
'leder',
'jeanshose',
'sweatshirt',
'sneakers',
'ledergürtel',
'kapuze',
'pullover',
'sneaker',
'armband',
'denim',
'hemd',
'shirt',
'sonnenbrille',
'sweatjacke',
'herrengürtel',
'winterjacke',
'belt',
'mütze',
'laufschuhe',
'biker',
'strickjake',
'chronograph',
'übergangsjacke',
'shorts',
'beanie',
'cap',
'parka',
'strickpullover',
'belt',
'mantel',
'hoody',
'tee',
't-shirt',
'longsleeve',
'steppjacke',
'kapuzenjacke',
'cargo',
'skinny',
'sweat',
'turnschuhe',
'jeansgürtel',
'fleece',
'langarmshirt',
'weste',
'leather',
'schmuck',
'jogginghose',
'bikerjeans',
'für',
'hoses',
'schuhe',
'boots',
'cardigan',
'poloshirt',
'sweater',
'uhren',
'sportjacke',
'steppweste',
'lederjacke',
'kurzmantel',
'tacket',
'trenchcoat',
'longshirt',
'sweatpants',
'unisex',
'damen',
'herren'
)

src = './outfit_products.csv'
data = pandas.DataFrame(columns=('id', 'href', 'categories', 'descriptor'))

with open(src, 'r', encoding='utf-8') as doc:
    rows = csv.reader(doc, delimiter=',')

    i = 0
    for row in rows:
        categories = row[1].replace('"', '').replace(',', ' ').strip()
        categories = re.sub('[-\'"\[\]+\./\(\):;|#\\\\]', '', categories)
        categories.strip()
        categories = str.lower(categories)

        d = ''
        id = row[0]
        href = row[2]
        for c in category:
            if c in categories:
                d += c + ','

        #if no sex is stated then it's unisex
        if len(d) > 0:
            if 'damen' not in d and 'herren' not in d and 'unisex' not in d:
                d += 'unisex,herren,damen'

        d = re.sub(',$', '', d) #Take out trailing comma
        print(id, href, d)
        data.loc[i] = [id, href, d, 'None']
        i += 1

data.to_csv('./data.csv', encoding='utf-8', index=False)
