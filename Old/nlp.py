'''
Natural Language Processing of Congressional Bills and Resolutions
Group Members: James Midkiff, Michelle Orden, Kelly Yang
nlp.py Code Author: James Midkiff
'''

# Dask Code, intended to be run on HPC such as Midway2 at UChicago
from dask_jobqueue import SLURMCluster
from dask.distributed import Client
from dask.dataframe import *
from dask.bytes import *
import sys
import dask
import boto3
import pandas as pd
import s3fs
import util

def extract_bill_info(data): 
    '''
    '''
    # Getting info about bills from bill id's
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

    # Util Functions
    data['subjectivity'] = data['text'].apply(util.subjectivity)#, meta=('text', 'float'))
    data['polarity'] = data['text'].apply(util.polarity)#, meta=('text', 'float'))

    data = data[['session', 'type', 'outcome', 'sponsor_count', 'section_count', 'word_count']]

    return data

def main(credentials): 
    s3 = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key'], 
        aws_session_token=credentials['aws_session_token'])

    # s3 = s3fs.core.S3FileSystem(
    #     key=credentials['aws_access_key_id'],
    #     secret=credentials['aws_secret_access_key'], 
    #     token=credentials['aws_session_token'])
    # with s3.open('s3://macs30123-bills/115_ids') as f: 
    #     file = f.read()
    #     print(type(file))
    #     d = read_bytes(f)
    #     # d = read_bytes(file)
    #     print(type(d),d)
    # AWS_DEFAULT_REGION='us-east-1'
    # AWS_ACCESS_KEY_ID=credentials['aws_access_key_id']
    # AWS_SECRET_ACCESS_KEY=credentials['aws_secret_access_key']
    # AWS_SESSION_TOKEN=credentials['aws_session_token']

    # read_json( # Does not work despite full public permissions - timeout error
    #     url_path='s3://macs30123-bills/115_ids', 
    #     anon=True) 
    # read_json( # Does not work despite full public permissions - timeout error
    #     url_path='s3://macs30123-bills/115_ids/test/115_ids.json', 
    #     storage_options={
    #         'key':credentials['aws_access_key_id'], 
    #         'secret':credentials['aws_secret_access_key'],
    #         'token':credentials['aws_session_token']}) 

    response = s3.list_objects(Bucket='macs30123-bills') # Can I convert this to a dataframe and run get_object that way?
    file_counter = 0
    for file in response['Contents']: # response is dict of object keys in S3
        name = file['Key']
        if 'bills' in name: 
            print(f'Extracting bills from {name}, file_counter: {file_counter}')
            d = s3.get_object(Bucket='macs30123-bills', Key=name)['Body'].read() # Get individual file
            d = pd.read_json(d) # Unable to figure out how to read the bytes stream without resorting to pandas
            session = d.columns[0] # Session number
            d['session'] = session
            d = d.rename(columns={session: 'text'}) # Rename to text
            
            if file_counter == 0: 
                data = from_pandas(d, npartitions=1) # Convert to Dask from Pandas DF
            else: 
                ddf = from_pandas(d, npartitions=1) # Convert to Dask from Pandas DF
                data = data.append(ddf)
            
            file_counter += 1

    data = extract_bill_info(data, name, s3)
    
    f = f'data.csv'
    data = data.compute()
    data.to_csv(f)
    s3.put_object(Bucket='macs30123-bills', Key=f)

n_cores = int(sys.argv[1])
credentials_file = str(sys.argv[2])
if __name__ == '__main__': 
    # module load python/anaconda-2019.03
    # scp 'D:\Everything\UChicago\Fall 2021\MACS 30123\Project\credentials.txt' "jmidkiff@midway2.rcc.uchicago.edu:/home/jmidkiff/PROJECT_MACS30123/credentials.txt" 
    # Compose SLURM script
    print(n_cores, '\n', credentials_file)
    credentials = {}
    with open(credentials_file, 'r', encoding='utf-8') as f:
        for line in f: 
            var, val = line.split(sep='=', maxsplit=1)
            val = val.rstrip('\n')
            print(var)
            print(val)
            credentials[var] = val
    
    cluster = SLURMCluster(queue='broadwl', cores=n_cores, memory='20GB', 
                        processes=n_cores, walltime='03:00:00', interface='ib0',
                        job_extra=['--account=macs30123'])

    cluster2 = SLURMCluster(queue='broadwl-lc', cores=n_cores, memory='20GB', 
                        processes=n_cores, walltime='03:00:00', interface='ib0',
                        job_extra=['--account=macs30123'])
    # Request resources
    cluster2.scale(jobs=1)

    client = Client(cluster2)
    print(client.dashboard_link)

    # Get data
    main(credentials)