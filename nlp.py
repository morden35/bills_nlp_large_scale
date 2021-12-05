'''
Natural Language Processing of Congressional Bills and Resolutions
Group Members: James Midkiff, Michelle Orden, Kelly Yang
nlp.py Code Author: James Midkiff
'''

# Dask Code, intended to be run on HPC such as Midway at UChicago
from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from dask.dataframe import *
from dask.bytes import *
import dask
import boto3
import pandas as pd

def extract_bill_info(data): 
    '''
    '''
    # Getting info about bills from bill id's
    bills = len(data) # Number of bills in file
    session = data.columns[0] # Session number
    data['session'] = session
    data = data.rename(columns={session: 'text'}) 
    data['type'] = (data.index.str.extract('((?<=\d)\D+(?=\d))')
        .to_dask_array(lengths=True).flatten())
    data['outcome'] = (data.index.str.extract('((?<=\d)\D+$)')
        .to_dask_array(lengths=True).flatten())

    # Cleaning up bill text
    data['text'] = data['text'].replace(to_replace=['<.*>', '&.*;', '\\\n'], value='', regex=True)
    data['text'] = data['text'].replace(to_replace=['\s{2,}'], value=' ', regex=True)

    # Getting count information
    data['sponsor_count'] = data['text'].str.count('Mr?s?\.[\s\-\w]*\.?[\s\-\w]*(?=[\s\(|,|\)])')
    data['section_count'] = data['text'].str.count('(?<![\'`])(?:SEC\.)\s\d+|(?:SECTION)\s\d+')
    # Only counts text after the following words appear
    pattern = "A BILL|RESOLUTION|AN ACT|An Act|AMENDMENT|"
    data['word_count'] = (data['text'].str.split(pat=pattern, n=1) 
        .apply(lambda x: x[1] if len(x) > 1 else x[0], meta=('text', 'object'))
        .str.count('\w+'))
    data = data[['session', 'type', 'outcome', 'sponsor_count', 'section_count', 'word_count']]
    data = data.compute()

    return data

def main(): 
    s3 = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=AWS_KEY_ID,
        aws_secret_access_key=AWS_SECRET, 
        aws_session_token=AWS_SESSION)

    response = s3.list_objects(Bucket='macs30123-bills')
    for file in response['Contents']: 
        name = file['Key']
        print(f'Extracting bills from {name}')
        if name.endswith('bills'): 
            data = s3.get_object(Bucket='macs30123-bills', Key=name)['Body'].read()
            data = pd.read_json(data) 
            data = from_pandas(data, npartitions=n_cores)
            data = extract_bill_info(data)
            break

if __name__ == '__main__': 
    n_cores=10
    # Compose SLURM script
    cluster = SLURMCluster(queue='broadwl', cores=n_cores, memory='5GB', 
                        processes=10, walltime='03:00:00', interface='ib0',
                        job_extra=['--account=macs30123'])

    # Request resources
    cluster.scale(jobs=1)

    client = Client(cluster)
    print(client.dashboard_link)

    # Get data
    AWS_KEY_ID = 'ASIASWCDU7BJZKKV5L6P'
    AWS_SECRET = 'Q3KtTcZY1RbQrCNvRE1pAqFg545t5oEatRit9EeC'
    AWS_SESSION = 'FwoGZXIvYXdzEKP//////////wEaDLXlpj9IsP7+UYUDwCLFAVoeKYXlvn5F6XmSqLHADKpU40KZQSSXnYKI2ujwKOvBiOu9pLvm5IrvB4o/yUJm2fE/h5cpqT2kOzgJVJGyPPUK+JxzBkH+8ydmbRdIKbEE7PDsZWxJLA9I0qxLGUYMl9jrNl8FlfNNn6SZCfd7EOtgQbFFFqPjQeRhAvqJjpep4miA/McfwXBvQXNI9MspJQ5psUUYV+70PO+rh+5/21VbMj2Kfa8gKWLcpINsI0RDZOXyuex3eHfejmhXzA7vTpLSX7JuKJ+5sI0GMi3gZeg5v5qxGMns7yjSU0tBC5i3fTsZqEIUuBtnpNdXx0Ngd9xNV8dKVxsXG8E='

    main()