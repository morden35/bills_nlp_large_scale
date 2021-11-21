import requests
import re

API_KEY = 'nt5nhSpwSqMbrGJ7hcsBkXFI1mfk80X0fexbnt45'

def get_offset():
    '''
    The govinfo API allows us to query 100 'collections' at a time. For a given
    congressional year, we need to call get_bill_ids() x times, depending on the
    number of total bills from that year. For example, Congress 116 had 20450,
    so we need to call 20450/100 = 205 times, changing the offset flag each time.
    '''
    
    total_bill_dict = {'116': 20450, '115': 18510, '114': 16092, '113': 13770, '112': 15162,
                        '111': 18231, '110': 19790, '109': 17403, '108': 15377, '107': 14882,
                        '106': 16052, '105': 13126, '104': 11434, '103': 14141}
    # total_bill_dict = {'116': 20450, '115': 18510, '114': 16092, '113': 13770, '112': 15162}
    # total_bill_dict = {'111': 18231, '110': 19790, '109': 17403, '108': 15377, '107': 14882}
    # total_bill_dict = {'106': 16052, '105': 13126, '104': 11434, '103': 14141}

    all_climate_bill_ids = {'116': [], '115': [], '114': [], '113': [], '112': [],
                            '111': [], '110': [], '109': [], '108': [], '107': [],
                            '106': [], '105': [], '104': [], '103': []}
    # all_climate_bill_ids = {'116': [], '115': [], '114': [], '113': [], '112': []}
    # all_climate_bill_ids = {'111': [], '110': [], '109': [], '108': [], '107': []}
    # all_climate_bill_ids = {'106': [], '105': [], '104': [], '103': []}

    for congress in total_bill_dict.keys():
        end_range = total_bill_dict[congress]
        # being limited at 9800 for all years
        # https://github.com/usgpo/api/issues/19#issuecomment-428292313
        for x in range(0, 9800, 100):
            subset_climate_bill_ids = get_bill_ids(offset=x, congress=congress)
            all_climate_bill_ids[congress].extend(subset_climate_bill_ids)
            # if len(subset_climate_bill_ids) > 0:
                # for c_id in subset_climate_bill_ids:
            # all_climate_bill_ids[] (c_id)
            print(x)
            # break

    print(all_climate_bill_ids)
    return get_package(all_climate_bill_ids)


def get_bill_ids(lastModifiedStartDate='1990-05-13T02:22:08Z', offset=0, pageSize=100, congress='116'):
    '''
    Given an offset value and congress number, this function makes a govinfo
    API call to request a list of 'collections' (bill ids). We will filter for
    bill ids that contain the word 'climate' or 'Climate' in the title.
    '''

    url = f'https://api.govinfo.gov/collections/BILLS/{lastModifiedStartDate}?offset={offset}&pageSize={pageSize}&congress={congress}&api_key={API_KEY}'
    # url = f'https://api.govinfo.gov/published/1990-01-01?offset={offset}&pageSize={pageSize}&collection=BILLS&congress={congress}&api_key={API_KEY}'
    PARAMS = {'headers': 'accept: application/json'}

    r = requests.get(url=url, params=PARAMS)
    
    data = r.json()
    # print(data.keys())

    # if len(data) > 1:
    packages = data['packages']
    climate_bill_ids = []
    for package in packages:
        if re.search(r"(C|c)limate", package['title']):
            climate_bill_ids.append(package['packageId'])
    # climate_bill_ids_dict = {congress: climate_bill_ids}
    
    # print(climate_bill_ids)
    return climate_bill_ids
    # return None


def get_package(all_climate_bill_ids):
    '''
    Given a list of bill ids (pre filtered for those that contain 'climate' in title),
    this function makes a govinfo API call to request the bill text.
    '''

    all_bills = {'116': {}, '115': {}, '114': {}, '113': {}, '112': {},
                '111': {}, '110': {}, '109': {}, '108': {}, '107': {},
                '106': {}, '105': {}, '104': {}, '103': {}}
    # all_bills = {'116': {}, '115': {}, '114': {}, '113': {}, '112': {}}
    # all_bills = {'111': {}, '110': {}, '109': {}, '108': {}, '107': {}}
    # all_bills = {'106': {}, '105': {}, '104': {}, '103': {}}

    for congress in all_climate_bill_ids.keys():
        for bill_id in all_climate_bill_ids[congress]:
            url = f'https://api.govinfo.gov/packages/{bill_id}/htm?api_key={API_KEY}'
            PARAMS = {'headers': 'accept: */*'}
            r = requests.get(url = url, params = PARAMS)
            # data = r.json()
            all_bills[congress][bill_id] = r.content
    
    # print(all_bills)
    # for key, val in all_bills.items():
    #     print(key)
    #     print(len(val))
        # congress - number of bills with 'climate' or 'Climate' in title (limited by first 10,000)
        # 116 - 50
        # 115 - 15
        # 114 - 16
        # 113 - 7
        # 112 - 11
        # 111 - 14
        # 110 - 20
        # 109 - 4
        # 108 - 2
        # 107 - 2
        # 106 - 3
        # 105 - 4
        # 104 - 0
        # 103 - 2

        # 150 total out of 140,000 searched (0.001%)
    return all_bills


if __name__ == '__main__':
    get_offset()

# this link is useful for defining terminology
# https://www.govinfo.gov/help/bills
# docClass: s (senate), hr (house), hres (houes simple resolution), sconres (senate concurrent resolution)
# billVersion: as, ash, ath, ats, cdh, cds, cph, cps, eah, eas, eh, enr.