import caffe
import pandas
import numpy as np
import cv2
from skimage import io

def find_descriptor(net, href):
    #read image
    try: img = io.imread(href) #Download url
    except: print('Link unavailable: ', href); log.append(href); return None
    #Preprocess
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) #Convert to BGR, it appears that the links are already BGR
    img = cv2.resize(img, (224, 224))
    #transformer
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1)) #input has shape 1,3,224,224
    transformer.set_mean('data', np.array([104, 117, 123]))
    img = transformer.preprocess('data', img)
    #Feed to network
    net.blobs['data'].data[...] = img
    out = net.forward()
    out = out['embedding'][0]
    out = [item for item in out] #Use this if storing descriptor as an array
    # out = ''.join('{},'.format(item) for item in out.astype(str))#[:-1]

    return out

#set network
net = caffe.Net('../deploy_googlenet-siamese.prototxt',
                '../googlenet-siamese-final.caffemodel',
                caffe.TEST)
data = pandas.read_csv('./data.csv', encoding='utf-8')
log = []

for i in range(0, len(data)):
    href = data.loc[i, 'href']
    try: descriptor = find_descriptor(net, href)
    except: print(i, ' ', href); data.to_csv('./data.csv', encoding='utf-8', index=False); log.append((i, href))
    print(i)
    data.loc[i, 'descriptor'] = descriptor

data.to_csv('./data.csv', encoding='utf-8', index=False)

with open('log.txt', 'w') as file:
 for item in log:
  file.write('{}\n'.format(item))


