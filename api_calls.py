import requests
import re

API_KEY = 'nt5nhSpwSqMbrGJ7hcsBkXFI1mfk80X0fexbnt45'

def get_offset():
    all_climate_bill_ids = []

    # 2016 congress had 20450 total bills
    # need to make 205 calls (max 100 packages per call)
    # for some reason, after 9800 not getting back 'packages'
    for x in range(0, 9800, 100):
        subset_climate_bill_ids = get_bill_ids(offset=x)
        if len(subset_climate_bill_ids) > 0:
            for c_id in subset_climate_bill_ids:
                all_climate_bill_ids.append(c_id)
        print(x)

    print(all_climate_bill_ids)
    # return all_climate_bill_ids
    return get_package(all_climate_bill_ids)


def get_bill_ids(lastModifiedStartDate='1990-05-13T02:22:08Z', offset=0, pageSize=100, congress='116'):

    url = f'https://api.govinfo.gov/collections/BILLS/{lastModifiedStartDate}?offset={offset}&pageSize={pageSize}&congress={congress}&api_key={API_KEY}'
    PARAMS = {'headers': 'accept: application/json'}

    r = requests.get(url = url, params = PARAMS)
    
    data = r.json()
    # print(data.keys())

    if len(data) > 1:
        packages = data['packages']
        climate_bill_ids = []
        for package in packages:
            if re.search(r"(C|c)limate", package['title']):
                climate_bill_ids.append(package['packageId'])
    
        # print(climate_bill_ids)
        return climate_bill_ids
    return None


def get_package(all_climate_bill_ids):
    all_bills = {}

    for bill_id in all_climate_bill_ids:
        url = f'https://api.govinfo.gov/packages/{bill_id}/htm?api_key={API_KEY}'
        PARAMS = {'headers': 'accept: */*'}
        r = requests.get(url = url, params = PARAMS)
        # data = r.json()
        all_bills[bill_id] = r.content
    
    print(all_bills)
    return all_bills


if __name__ == '__main__':
    get_offset()
