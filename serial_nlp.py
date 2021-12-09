'''
Natural Language Processing of Congressional Bills and Resolutions
Group Members: James Midkiff, Michelle Orden, Kelly Yang
serial_nlp.py Code Author: James Midkiff
'''

import sys
import boto3
import pandas as pd
import util
import time

def extract_bill_info(data): 
    # Getting info about bills from bill id's
    data['type'] = data.index.str.extract('(?<=\d)(\D+)(?=\d)', expand=False)
    data['outcome'] = data.index.str.extract('((?<=\d)\D+$)', expand=False)

    # Getting count information
    data['sponsor_count'] = data['text'].str.count('Mr?s?\.[\s\-\w]*\.?[\s\-\w]*(?=[\s\(|,|\)|<])')
    data['section_count'] = data['text'].str.count('<section') # Technically it's sections and sections revised in other laws
    
    # Cleaning up bill text
    data['text'] = (data['text'].replace(
        to_replace=['<.*?>', '&.*?;', '\\n', '\\t', r'\\u\d+'], 
        value='', regex=True))
    data['text'] = data['text'].replace(to_replace=['\s{2,}'], value=' ', regex=True)

    # Only counts text after the following words appear:
    pattern = "A BILL|RESOLUTION|AN ACT|An Act|AMENDMENT|CONCURRENT RESOLUTION"
    data['word_count'] = (data['text'].str.split(pat=pattern, n=1) 
        .apply(lambda x: x[1] if len(x) > 1 else x[0])
        .str.count('\w+'))

    print(data.head(),'\n')
    
    # Util Functions
    print(f"    Running Util Functions for {data.iloc[0]['session']}")
    data['subjectivity'] = data['text'].apply(util.subjectivity)
    data['polarity'] = data['text'].apply(util.polarity)

    data = data[[
        'session', 'type', 'outcome', 'sponsor_count', 'section_count', 'word_count', 
        'subjectivity', 'polarity']]
    
    return data

def main(credentials): 
    # Initialize s3 client with credentials
    s3 = boto3.client('s3',
        region_name='us-east-1',
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key'], 
        aws_session_token=credentials['aws_session_token'])
    response = s3.list_objects(Bucket='macs30123-bills') # Can I convert this to a dataframe and run get_object that way?
    
    start = time.time()
    file_counter = 0
    r_df = pd.DataFrame()
    for file in response['Contents']: # response is dict of object keys in S3
        name = file['Key']
        if 'bills' in name and 'csv' not in name: 
            print(f'Extracting bills from {name}, file_counter: {file_counter}')
            d = s3.get_object(Bucket='macs30123-bills', Key=name)['Body'].read() # Get individual file
            d = pd.read_json(d) 
            session = d.columns[0] # Session number
            d['session'] = session
            d = d.rename(columns={session: 'text'}) # Rename to text
            
            data = extract_bill_info(d)
            r_df = r_df.append(data)
            print(f'***** r_df.head()\n, {r_df.head()}')
            file_counter += 1
    
    end = time.time()
    print(f'\nRequired {round(end-start, 2)} to process')
    
    # Print to CSV and then upload to S3
    r_df.to_csv('data_bills.csv')
    s3.upload_file(Filename='data_bills.csv', Bucket='macs30123-bills', Key='data.csv', 
        ExtraArgs={'ACL':'public-read'})

# Entry point for file. Must run in same location as credentials file, inputting 
# credentials file as command line argument
# I.e. run the following from the command line after updating credentials: 
# python credentials.txt
credentials_file = str(sys.argv[1])
if __name__ == '__main__': 
    # Load Credentials as a system argument
    credentials = {}
    with open(credentials_file, 'r', encoding='utf-8') as f:
        for line in f: 
            var, val = line.split(sep='=', maxsplit=1)
            val = val.rstrip('\n')
            print(var)
            print(val)
            credentials[var] = val
    
    # Get data
    main(credentials)