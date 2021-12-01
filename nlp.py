'''
Natural Language Processing of Congressional Bills and Resolutions
Group Members: James Midkiff, Michelle Orden, Kelly Yang
nlp.py Code Author: James Midkiff
'''

# Dask Code, intended to be run on HPC such as Midway at UChicago
from dask_jobqueue import SLURMCluster

# Compose SLURM script
cluster = SLURMCluster(queue='broadwl', cores=10, memory='5GB', 
                       processes=10, walltime='03:00:00', interface='ib0',
                       job_extra=['--account=macs30123'])

# Request resources
cluster.scale(jobs=1)

from dask.distributed import Client

client = Client(cluster)
print(client.dashboard_link)

# Get data
from dask.dataframe import *

data = read_json(
    url_path='/home/jmidkiff/PROJECT_MACS30123/climate_bills/115_bills.json', 
    lines=False)

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
