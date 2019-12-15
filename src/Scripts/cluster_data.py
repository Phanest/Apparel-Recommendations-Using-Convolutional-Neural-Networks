import numpy as np
from neo4j.v1 import GraphDatabase
from sklearn.cluster import KMeans
import os

def get_categories(session):
    query = "MATCH (c:Category)" \
            "RETURN DISTINCT c.name"
    results = session.run(query) #check usage, does it return a list of strings
    results = results.value() #returns list with results

    #check how to remove these values
    results.remove('damen')
    results.remove('herren')
    results.remove('unisex')

    return results

def splice_data(data):
    ids = []
    descriptors = []

    for record in data:
        node = record['a']
        id = node['id']
        descriptor = node['descriptor']
        #Take out []
        descriptor = descriptor[1:]
        descriptor = descriptor[:-1]
        #Turn to array
        descriptor = np.fromstring(descriptor, dtype=np.float32, sep=',')

        ids.append(id)
        descriptors.append(descriptor)

    descriptors = np.array(descriptors) #Check in clustering example

    return ids, descriptors

def get_results(session, category, gender):
    query = 'MATCH (a:Item) -[:HAS_CATEGORY]-> (b:Category {name:{category}}),' \
            '(c:Category {name:{gender}}) <-[:HAS_CATEGORY]- (a)' \
            'RETURN a'
    results = session.run(query, category=category, gender=gender)
    return results

def add_results(session, ids, labels, centroids, category, gender):
    for i in range(0, len(ids)):
        id = ids[i]
        label = labels[i]
        centroid = centroids[label]
        centroid = centroid.tolist()

        query = 'MERGE (a:Item {id:{id}}) ' \
                'MERGE (b:Centroid {category:{category}, gender:{gender}, descriptor:{centroid}}) ' \
                'MERGE (a) -[:GRAVITATES]-> (b)'
        session.run(query, id=id, category=category, gender=gender, centroid=centroid)

def cluster(session, category, gender):
    results = get_results(session, category, gender)
    ids, descriptors = splice_data(results)

    length = len(ids)
    clusters = 20
    if length <= 50: #We don't really need clusters in this case
        return
    if length <= 500:
        clusters = 10

    kmeans = KMeans(n_clusters=clusters).fit(descriptors)
    print('Clustered')

    try:add_results(session, ids, kmeans.labels_, kmeans.cluster_centers_, category, gender)
    except: print('failed: ', category, ' ', gender)
    print(category, ' ', gender, ' added!')

uri = 'bolt://0.0.0.0:7472'
# password = os.getenv('NEO4J_PASSWORD')
password = 'starlight'

driver = GraphDatabase.driver(uri, auth=('neo4j', password))
session = driver.session()

categories = get_categories(session)

for category in categories:
    for gender in ['damen', 'herren', 'unisex']:
        print(category, ' ', gender)
        cluster(session, category, gender)
