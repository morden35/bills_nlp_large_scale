import requests
import re
import time
import json
import sys
import boto3

# Initialize Boto Client for S3
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
bucket_resource = s3_resource.Bucket('macs30123-bills')

API_KEY = 'nt5nhSpwSqMbrGJ7hcsBkXFI1mfk80X0fexbnt45'

def get_offset(congress="116"):
    '''
    The govinfo API allows us to query 100 'collections' at a time. For a given
    congressional year, we need to call get_bill_ids() x times, depending on the
    number of total bills from that year. For example, Congress 116 had 20450,
    so we need to call 20450/100 = 205 times, changing the offset flag each time.

    This function iterates through docClass, billVersion, and offset values and
    calls get_bill_ids() for each combination.

    Inputs:
        congress (str) - the congress number we want to query (default is 116)
    Returns:
        get_package(all_bill_ids, congress) - This function calls the
            get_package() function which will get all bill texts for the list
            of all_bill_ids

    This function also writes all all_bill_ids to json file.
    '''

    # all_bill_ids = {'116': [], '115': [], '114': [], '113': [], '112': [],
    #                         '111': [], '110': [], '109': [], '108': [], '107': [],
    #                         '106': [], '105': [], '104': [], '103': []}

    all_bill_ids = {congress: []}

    docClass = ['s', 'hr', 'hres', 'sconres']
    billVersion = ['as', 'ash', 'ath', 'ats', 'cdh', 'cds', 'cph', 'cps', 'eah',
                   'eas', 'eh', 'eph', 'phs', 'enr', 'es', 'fah', 'fph', 'fps',
                   'hdh', 'hds', 'ih', 'iph', 'ips', 'is', 'lth', 'lts', 'oph',
                   'ops', 'pav', 'pch', 'pcs', 'pp', 'pap', 'pwah', 'rah',
                   'ras', 'rch', 'rcs', 'rdh', 'rds', 'reah', 'res', 'renr',
                   'rfh', 'rfs', 'rh', 'rih', 'ris', 'rs', 'rth', 'rts', 'sas',
                   'sc']

    start_time = time.time()
    # for num2, dclass in enumerate(docClass): # 4 loops
        # for num3, version in enumerate(billVersion): # 53 loops
    dclass = "hr"
    version = "ih"
    # print(f"{((len(billVersion)*num2)+(num3 + 1))/(len(docClass)*len(billVersion))*100}% done")
    now = time.time()
    # print(f"{((num2 * num3) / 212)*100}% done")
    # print(f"{(now - start_time)/60} minutes elapsed")
    # being limited at 10000 for all years
    # https://github.com/usgpo/api/issues/19#issuecomment-428292313
    for x in range(0, 10000, 100): # 100 loops
        print(x)
        subset_bill_ids = get_bill_ids(offset=x,
                                                congress=congress,
                                                docClass=dclass,
                                                billVersion=version)
        if subset_bill_ids:
            all_bill_ids[congress].extend(subset_bill_ids)

    print(all_bill_ids)
    # NEEDS TO GO IN S3
    # bucket_resource.put_object(all_bill_ids)
    bucket_resource.put_object(Key=f'{congress}', Body=json.dumps(all_bill_ids))

    print("check bucket")
    # with open(f'bill_ids/{congress}_ids.json', 'w') as outfile:
        # json.dump(all_bill_ids, outfile)
    return get_package(all_bill_ids, congress)


def get_bill_ids(lastModifiedStartDate='1990-05-13T02:22:08Z',
                 offset=0,
                 pageSize=100,
                 congress='116',
                 docClass='s',
                 billVersion='is'):
    '''
    Given an offset value and congress number, this function makes a govinfo
    API call to request a list of 'collections' (bill ids). We will filter for
    bill ids that contain the word 'climate' or 'Climate' in the title.

    Inputs:
        lastModifiedStartDate (str) - This is the start date and time in
            ISO8601 format (yyyy-MM-dd'T'HH:mm:ss'Z')
        offset (int) - This is the starting record you wish to retrieve
        pageSize (int) - The number of records you would like to return within
            a given request
        congress (str) - congress number (116 default)
        docClass (str) - bill/collection categories (s, hr, hres, sconres)
        billVersion (str) - the bill version (there are 53 possible types)
    Returns:
        climate_bill_ids (list) - list of bill_ids that contain 'climate' or
            'Climate' in the title
        returns None if the API call results in bad status code
    '''

    url = f'https://api.govinfo.gov/collections/BILLS/{lastModifiedStartDate}?offset={offset}&pageSize={pageSize}&congress={congress}&docClass={docClass}&billVersion={billVersion}&api_key={API_KEY}'
    PARAMS = {'headers': 'accept: application/json'}

    r = requests.get(url=url, params=PARAMS)
    if r.status_code == 200:
        data = r.json()

        packages = data['packages']
        # climate_bill_ids = []
        # for package in packages:
            # if re.search(r"(C|c)limate", package['title']):
                # climate_bill_ids.append(package['packageId'])
        # climate_bill_ids_dict = {congress: climate_bill_ids}
        
        # print(climate_bill_ids)
        return packages
    return None


def get_package(all_bill_ids, congress):
    '''
    Given a list of bill ids (pre filtered for those that contain 'climate' in
    title), this function makes a govinfo API call to request the bill text.

    Inputs:
        all_bill_ids (dict) - A dictionary with the congress number as
            the key, and a list of climate_bill_ids (list of bill ids) as the
            value
        congress (str) - the congress number
    Returns:
        This function dumps a dictionary of dictionaries to
        climate_bills/{congress}_bills.json. The dictionary key is the congress
        number. The dictionary value is another nested dictionary. The nested
        dictionary keys are the bill ids. The nested dictionary values are the
        bill text.
    '''
    all_bills = {congress: {}}
    # all_bills = {'116': {}, '115': {}, '114': {}, '113': {}, '112': {},
    #             '111': {}, '110': {}, '109': {}, '108': {}, '107': {},
    #             '106': {}, '105': {}, '104': {}, '103': {}}

    # for congress in all_bill_ids.keys():
    for package in all_bill_ids[congress]:
        bill_id = package["packageId"]
        # url = f"https://api.govinfo.gov/packages/{bill_id}/summary?api_key={API_KEY}"
        url = f'https://api.govinfo.gov/packages/{bill_id}/htm?api_key={API_KEY}'
        PARAMS = {'headers': 'accept: */*'}
        # PARAMS = {'headers': 'accept: application/json'}
        r = requests.get(url = url, params = PARAMS)
        # need to decode the bytes object
        # bill_summary = json.loads(r.content)
        # bill_text = json.loads(r.content)["download"]["txtLink"]
        all_bills[congress][bill_id] = r.content.decode('utf8')

    # NEEDS TO GO IN S3
    with open(f'bills/{congress}_bills.json', 'w') as outfile:
        json.dump(all_bills, outfile)
    # return all_bills


if __name__ == '__main__':
    congress = sys.argv[1]
    get_offset(congress)

# this link is useful for defining terminology
# https://www.govinfo.gov/help/bills
