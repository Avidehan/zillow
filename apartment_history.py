import csv
import datetime
import requests
from bs4 import BeautifulSoup

headers = {
    'authority': 'www.zillow.com',
    'accept': '*/*',
    'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
    'client-id': 'home-details_fs-sp_home-value-v2-zestimate-summary_home-value-v2-zestimate-summary',
    'origin': 'https://www.zillow.com',
    'referer': 'https://www.zillow.com/homedetails/24406-Poinsettia-Dr-Lake-Elsinore-CA-92532/303945064_zpid/',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}


def get_zipid_from_url(url):
    arr_url = url.split('/')

    return arr_url[-2][:-5]


def get_history(zipid):
    json_data = {
        'query': 'query HomeValueChartDataQuery($zpid: ID!, $metricType: HomeValueChartMetricType, $timePeriod: HomeValueChartTimePeriod, $useNewChartAPI: Boolean) {\n  property(zpid: $zpid) {\n    homeValueChartData(metricType: $metricType, timePeriod: $timePeriod, useNewChartAPI: $useNewChartAPI) {\n      points {\n        x\n        y\n      }\n      name\n    }\n  }\n}\n',
        'operationName': 'HomeValueChartDataQuery',
        'variables': {
            'zpid': zipid,
            'timePeriod': 'TEN_YEARS',
            'metricType': 'LOCAL_HOME_VALUES',
            'forecast': True,
            'useNewChartAPI': False,
        },
        'clientVersion': 'home-details/6.1.843.master.41c3b72',
    }
    params = {
        'zpid': f'{zipid}',
        'contactFormRenderParameter': '',
        'queryId': '5582b563887a055bb98be6388c7f81bd',
        'operationName': 'ForSaleShopperPlatformFullRenderQuery',
    }

    return requests.post('https://www.zillow.com/graphql/', params=params, headers=headers, json=json_data).json()


def get_current_value(zipid):
    json_data = {
        'operationName': 'ForSaleShopperPlatformFullRenderQuery',
        'variables': {
            'zpid': zipid,
            'contactFormRenderParameter': {
                'zpid': zipid,
                'platform': 'desktop',
                'isDoubleScroll': True,
            },
        },
        'clientVersion': 'home-details/6.1.843.master.41c3b72',
        'queryId': '5582b563887a055bb98be6388c7f81bd',
    }
    params = {
        'zpid': f'{zipid}',
        'contactFormRenderParameter': '',
        'queryId': '5582b563887a055bb98be6388c7f81bd',
        'operationName': 'ForSaleShopperPlatformFullRenderQuery',
    }
    return requests.post('https://www.zillow.com/graphql/', params=params, headers=headers, json=json_data).json()


def get_history_by_url(url):
    data = {}
    zipid = get_zipid_from_url(url)
    print(zipid)
    if get_history(zipid)['data']['property']['homeValueChartData']:
        for data_history in get_history(zipid)['data']['property']['homeValueChartData'][0]['points']:
            value = data_history['y']
            date = datetime.datetime.fromtimestamp(int(data_history['x']) / 1000.0)
            month = date.strftime("%B")
            year = date.strftime("%Y")
            history_label = "Historical " + month + ' ' + year
            data[f'{history_label}'] = value
    address = ''
    static = get_current_value(zipid)
    current_value = static['data']['property']['adTargets']['price']

    for prop_address in static['data']['property']['address'].values():
        if prop_address:
            address += prop_address + ' '

    data["current value"] = current_value
    data["address"] = address
    return data




if __name__ == "__main__":
    url = 'https://www.zillow.com/homes/32022-Poppy-Way-Lake-Elsinore,-CA-92532_rb/17937295_zpid/'
    arr_url = url.split('/')
    data = get_history_by_url(url)
    with open(f'{arr_url[-3]}.csv', 'w', newline='') as csvfile:
        header_key = [field for field in data.keys()]
        new_val = csv.DictWriter(csvfile, fieldnames=header_key)
        new_val.writeheader()
        new_val.writerow(data)









"""*********************************************** tests ************************************************************"""


def get_all_zipid():
    response = requests.get('https://www.zillow.com/homes/for_sale/', headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.findAll("article")
    return [i['id'][5:] for i in article]


def test_all_zipid():
    for zipid in get_all_zipid():
        if get_history(zipid)['data']['property']['homeValueChartData']:
            for data_history in get_history(zipid)['data']['property']['homeValueChartData'][0]['points']:
                value = data_history['y']
                date = datetime.datetime.fromtimestamp(int(data_history['x']) / 1000.0)
                month = date.strftime("%B")
                year = date.strftime("%Y")
                print(value, year, month)
        address = ''
        static = get_current_value(zipid)
        current_value = static['data']['property']['adTargets']['price']
        for prop_address in static['data']['property']['address'].values():
            if prop_address:
                address += prop_address + ' '

        print(address, current_value)
