import numpy as np
from neo4j.v1 import GraphDatabase
from sklearn.cluster import KMeans
import os
import sys
import caffe
from sklearn.neighbors import NearestNeighbors
from skimage import io
import cv2

def find_descriptor(net, href):
    #read image
    try: img = io.imread(href) #Download url
    except: print('Link unavailable: ', href); return None
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

def find_nearest_centroid(session, queried_descriptor, category, gender, nearest=3):
    query = 'MATCH (a:Centroid)' \
            'WHERE a.category = {category} AND a.gender = {gender}' \
            'RETURN a.descriptor as descriptor'
    result = session.run(query, category=category, gender=gender)
    
    if result.peek() is None:
        return None
    
    descriptors = []
    for item in result:
        descriptor = item['descriptor']

        descriptors.append(descriptor)
    
    NN = NearestNeighbors(n_neighbors=5, radius=10000)
    NN.fit(descriptors)
    index = NN.kneighbors([queried_descriptor], return_distance=False)[0, nearest]
    
    return descriptors[index]
    
def get_links(links, indexes):
    neighbours = []
    for i in range(0, indexes.size):
        index = indexes[0, i]
        neighbours.append(links[index])
    return neighbours

def knn(session, queried_descriptor, centroid, category, gender, neighbours=5):
    if centroid is not None:
        query = 'MATCH (a:Item) -[:GRAVITATES]-> (b:Centroid)' \
                'WHERE b.category = {category} AND b.gender = {gender} AND b.descriptor = {centroid}' \
                'RETURN a'
        result = session.run(query, category=category, gender=gender, centroid=centroid)
    else:
        query = 'MATCH (c:Category) <-[:HAS_CATEGORY]- (a:Item) -[:HAS_CATEGORY]-> (b:Category) ' \
                'WHERE c.category = {category} AND b.gender = {gender}' \
                'RETURN a'
        result = session.run(query, category=category, gender=gender)
    
    descriptors = []
    links = []
    for item in result:
        node = item['a']
        descriptor = toArray(node['descriptor'])
        link = node['link']
        
        descriptors.append(descriptor)
        links.append(link)
    
    NN = NearestNeighbors(n_neighbors=neighbours, radius=10000)
    NN.fit(descriptors)
    indexes = NN.kneighbors([queried_descriptor], return_distance=False)
    matches = get_links(links, indexes)

    return matches

def find_descriptor_from_id(session, id):
    query = 'MATCH (a:Item)' \
            'WHERE a.id = {id}' \
            'RETURN a.descriptor as descriptor, a.link as link'
    result = session.run(query, id=id)
    result = result.single()

    try: 
        descriptor = toArray(result['descriptor'])
        link = result['link']
    except:
        return None, None
    
    return descriptor, link

#Turns a string descriptor to a numpy array
def toArray(descriptor):
    descriptor = descriptor[1:]
    descriptor = descriptor[:-1]
    descriptor = np.fromstring(descriptor, dtype=np.float32, sep=',')
    return descriptor
    

def plotItems(item, matches, UI=True):
    if UI:
        pass
    else:
        print('Query: {}'.format(item))
        print('Matches: {}'.format(matches))

def get_descriptor(session, net, item):
    if item.isdigit():
        item = int(item)
        descriptor, link = find_descriptor_from_id(session, item)
    else:
        descriptor = find_descriptor(net, item)
        descriptor = np.array(descriptor, dtype=np.float32)
        link = item
    
    if descriptor is None:
        raise Exception('Could not find descriptor for item: {}'.format(item))
    return descriptor, link

#Because some categories are intermixed, using the first cluster gives us items from the same category as ours,
#we try to avoid that by using the nearest variable which tells us which nth nearest cluster to use
def find_matches(session, descriptor, category, gender, nearest=1):
    #Some categories don't have centroids
    if nearest > 5:
        print('nearest can\'t be bigger than 5, setting to 5!')
        nearest = 5
    centroid = find_nearest_centroid(session, descriptor, category, gender, nearest=nearest-1)
    items = knn(session, descriptor, centroid, category, gender)
    return items

uri = 'bolt://0.0.0.0:7472'
password = 'starlight'
nearest = 1

driver = GraphDatabase.driver(uri, auth=('neo4j', password))
session = driver.session()

#Initialize net
net = caffe.Net('../deploy_googlenet-siamese.prototxt',
                '../googlenet-siamese-final.caffemodel',
                caffe.TEST)

while True:

    nearest = int(input('Which centroid (1st, 2nd, 3rd...) should be taken into account?\n'))
    item = input('Query item (id or link): ')
    category = input('Matches from category: ')
    gender = input('Gender:')

    # We get the descriptor describing our item, whether it's an id in our database or a link
    descriptor, link = get_descriptor(session, net, item)


    matches = find_matches(session, descriptor, category, gender, nearest)
    plotItems(link, matches, UI=False)
