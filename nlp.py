'''
Natural Language Processing of Congressional Bills and Resolutions
Group Members: James Midkiff, Michelle Orden, Kelly Yang
nlp.py Code Author: James Midkiff
'''

# Dask Code, intended to be run on HPC such as Midway at UChicago
from dask_jobqueue import SLURMCluster
n_cores=10
# Compose SLURM script
cluster = SLURMCluster(queue='broadwl', cores=n_cores, memory='5GB', 
                       processes=10, walltime='03:00:00', interface='ib0',
                       job_extra=['--account=macs30123'])

# Request resources
cluster.scale(jobs=1)

from dask.distributed import Client

client = Client(cluster)
print(client.dashboard_link)

# Get data
from dask.dataframe import *
from dask.bytes import *
import pandas as pd

AWS_KEY_ID = 'ASIASWCDU7BJUUJRTDVX'
AWS_SECRET = 'rIPn8ehqgtkyOEscAC6TzOaJLQJ4Ntncfvlu/xXE'
AWS_SESSION = 'FwoGZXIvYXdzEJ///////////wEaDIrprrHTSilxUymc+iLFAZIqdXBMeUPmPu8h1furDXZr1AWNihZT3udwhiM2pa1NW34qyeIMyBcKQ+Sn6QrEEImiZYrZrs5fL6A0F9+8NiIw1X1m4mh1KfkXSQz9EYR/4hdGd6KfIwkY71esb3Sd7wMrCrHTyh63Nmceglwp3kGesnvGiW0eCafjAyNHtmMYvoE0A5KaSWT8M2oJhHLSv+KFFi6oudZC5mnuJdGDwajGsenqgT0KXN/4k7X8U/bDK47STBOWR3vuvV55mVtZKwSeKlNsKKizr40GMi0O1P63wJ7tG2CViSN0VCl0Sk1ENJqzc6YHGBlJ1hqxYKMmSEZz9IbS+SUPc4A='

import boto3
s3 = boto3.client('s3',
    region_name='us-east-1',
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET, 
    aws_session_token=AWS_SESSION)
response = s3.list_objects(Bucket='macs30123-bills')
for file in response['Contents']: 
    name = file['Key']
    print(name)
    if name.endswith('bills'): 
        obj = s3.get_object(Bucket='macs30123-bills', Key=name)['Body'].read()
        data = pd.read_json(obj) 
        data = from_pandas(data, npartitions=n_cores)
        break

def extract_bill_info(data,): 
    '''
    '''
    # Getting info about bills from bill id's
    bills = len(data) # Number of bills in file
    session = data.columns[0] # Session number
    data['session'] = session
    data = data.rename(columns={session: 'text'}) 
    data['type'] = (data.index.str.extract('((?<=\d)\D+(?=\d))')
        .to_dask_array(lengths=(bills,)).flatten())
    data['outcome'] = (data.index.str.extract('((?<=\d)\D+$)')
        .to_dask_array(lengths=(bills,)).flatten())

    # Cleaning up bill text
    data['text'] = data['text'].replace(to_replace=['<.*>', '&.*;', '\\\n'], value='', regex=True)
    data['text'] = data['text'].replace(to_replace=['\s{2,}'], value=' ', regex=True)

    # Getting count information
    data['sponsor_count'] = data['text'].str.count('Mr?s?\.[\s\-\w]*\.?[\s\-\w]*(?=[\s\(|,|\)])')
    data['section_count'] = data['text'].str.count('(?<![\'`])(?:SEC\.)\s\d+|(?:SECTION)\s\d+')
    data['word_count'] = (data['text'].str.split(pat="A BILL|RESOLUTION", n=1) # Only counts text after the words 'A BILL' or 'RESOLUTION' appear
        .apply(lambda x: x[1], meta=('text', 'object'))
        .str.count('\w+'))
