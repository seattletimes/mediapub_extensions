from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from multiprocessing.dummy import Pool as ThreadPool
import os
import json

class GoogleAnalytics(object):
    verbose = False
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    VIEW_ID = None
    analytics = None
    requests = []

    def __init__(self, keyfile, view_id, verbose=False):
        self.verbose=verbose
        self.KEY_FILE_LOCATION = keyfile
        self.VIEW_ID = view_id
        if self.verbose: print("connecting to Google Analytics.... ")
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.KEY_FILE_LOCATION, self.SCOPES)
        self.analytics = build('analytics', 'v4', credentials=credentials)
        if self.verbose: print("Google Analytics connected. ")

    def multithreaded_query(self, params):
        result = self.analytics.reports().batchGet(body={'reportRequests': self.build_query(params)}).execute()
        return result

    def add_query_to_request(self, params):
        self.requests.append(self.build_query(params))

    def send_requests(self):
        result = self.analytics.reports().batchGet(body={'reportRequests': self.requests}).execute()
        self.requests = []
        return result

    def build_query(self, params):
        reportrequest = {}
        reportrequest['dateRanges'] = []
        reportrequest['metrics'] = []
        reportrequest['dimensions'] = []
        reportrequest['samplingLevel'] = 'LARGE'  # TODO: make this configurable
        reportrequest['pageSize'] = 10000 # TODO: make this configurable

        reportrequest['viewId'] = params['viewId'] if 'viewId' in params else self.VIEW_ID

        if 'date' in params:
            reportrequest['dateRanges'].append(params['date'])
        else:
            reportrequest['dateRanges'].append({'startDate': '30daysAgo', 'endDate': 'today'})

        for dim in params['dimensions']:
            reportrequest['dimensions'].append({'name': dim})

        for metric in params['metrics']:
            reportrequest['metrics'].append({'expression': metric})

        if 'filters' in params:
            reportrequest['dimensionFilterClauses'] = []
            holder = {}
            clauses = []

            for item in params['filters']:
                condition = {}
                condition['dimensionName'] = item
                condition['operator'] = 'PARTIAL' #'EXACT'
                condition['expressions'] = params['filters'][item]
                clauses.append(condition)

            holder['filters'] = clauses

            # TODO: find out how to pass an or in a simple way
            if len(params['filters']) > 0:
                holder['operator'] = 'AND'

            reportrequest['dimensionFilterClauses'].append(holder)
        # if self.verbose: print(reportrequest)
        return reportrequest

    def parse_response(self, response):
        resp = []
        for report in response['reports']:
            resp.append(self.build_response_object(report))
        return resp

    def build_response_object(self, response):
        results = []
        columnHeader = response.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in response.get('data', {}).get('rows', {}):
            dimensions = row.get('dimensions', [])
            values = row.get('metrics', [])
            rowValues = {}
            for header, dimension in zip(dimensionHeaders, dimensions):
                header = self.cleanHeaders(header)
                rowValues[header] = dimension
            for i, values in enumerate(values):
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    mHeader = self.cleanHeaders(metricHeader.get('name'))
                    rowValues[mHeader] = value
            results.append(rowValues)

        jsnResults = json.dumps(results, indent=4)
        parsed = json.loads(jsnResults)
        return parsed

    def cleanHeaders(self, header):
        if header == 'ga:dimension6':
            header = 'tags'
        elif header == 'ga:dimension18':
            header = 'articleId'
        elif header == 'ga:dimension14':
            header = 'role'
        elif header == 'ga:dimension40':
            header = 'pubDate'
        elif header == 'ga:dimension41':
            header = 'lastModifiedDate'
        elif header == 'ga:dimension2':
            header = 'author'
        elif header == 'ga:dimension17':
            header = 'title'
        elif header == 'ga:avgTimeOnPage':
            header = 'avgTimeOnPage'
        else:
            header = header.strip("ga:")
        return header

    def cleanValues(self, val):
        val = val.replace('&#039;', "'")
        return val


if __name__=='__main__':
    import datetime

    ga = GoogleAnalytics(key_path, '91048887', verbose=True)

    queries = {
        'metrics': ['ga:pageviews', 'ga:users'],
        'dimensions': [
            'ga:date',
            # 'ga:dimension18', # articleId
            # 'ga:dimension40', # pubdate
        ],
        'filters': {'ga:date': datetime.datetime.now().strftime("%Y%m%d")}
    }
    ga.add_query_to_request(queries)
    resp = ga.send_requests()
    print(resp)
    results = ga.parse_response(resp)
    print(results)
