from googleads import ad_manager
from googleads import oauth2
import tempfile
import googleads.errors
import csv

class GoogleAdManager(object):
    """
    Handles connections and queries to Google Ad Manager

    This class handles connections to Google Ad Manager and runs requests and queries.

    Requires:
        googleads: pip install googleads

    Attributes:
        client (googleads.ad_manager.AdManagerClient): The Ad Manager Connection
        verbose (bool): The verbosity flag
    """

    client = None
    verbose = False


    #********************************************************
    # Connection Methods
    #********************************************************

    def __init__(self, credentials_file=None, verbose=False):
        """
        Create an Ad Manager connection

        Args:
            credentials_file (str): The Google API Keyfile path
            verbose (bool): Should output be printed to stdout

        Yields:
            googleads.ad_manager.AdManagerClient: An Ad Manager Connection
        """

        self.verbose = verbose
        if self.verbose: print("Initializing Google Ad Manager...")
        # If the Google API key is passed, use it to build a connection, otherwise look for the YAML
        if credentials_file: self.client = self._oauth2_client(credentials_file)
        else: self.client = ad_manager.AdManagerClient.LoadFromStorage()
        if self.verbose: print("done.\n")

    def _oauth2_client(self, credentials_file, application_name="The Seattle Times DFP"):
        """
        Create a client given a Google API Keyfile.
        """

        #NOTE: created this function to move things out of the constructor, but
        #NOTE: (cont) we may want to move all of the client functions here.
        oauth2_client = oauth2.GoogleServiceAccountClient(credentials_file, oauth2.GetAPIScope('ad_manager'))
        ad_client = ad_manager.AdManagerClient(oauth2_client, application_name)
        return ad_client

    #***************************************************************************
    # General Methods
    #***************************************************************************

    def get_all_networks(self):
        """ Get a List of all Networks on the Account"""
        networks = self.client.GetService("NetworkService").getAllNetworks()
        return networks

    def get_current_network(self):
        """ Get a the Current Network Set on the Account"""
        network = self.client.GetService("NetworkService", version='v201808').getCurrentNetwork()
        return network

    def set_current_network(self):
        """
        Sets the Network
        """
        #TODO: Do this!!
        raise NotImplementedError

    #***************************************************************************
    # Data Request Methods
    #***************************************************************************

    def run_pql(self, query, version='v201808'):
        """
        Run a PQL query

        When given a PQL query, run it against the Ad Manager and return the results
        as a List.  Methods to create a csv are not implemented and left to the client
        since this code does not run from a set location.

        Args:
            query (str): The Query to run
            version (str): The version number the query is written in

        Returns:
            List: A list of the results.  The names are in the first element.

        Resources:
            https://developers.google.com/ad-manager/api/pqlreference
            https://developers.google.com/ad-manager/api/deprecation
        """
        data_downloader = self.client.GetDataDownloader(version)
        resp = data_downloader.DownloadPqlResultToList(query)
        return resp

    def run_request(self, report_job, version='v201808'):
        """
        Run an Ad Exchange request

        Run a custom Ad Exchange request and wait for the results.

        Args:
            report_job (dict): The request object
            version (str): The version number the request is written in

        Returns:
            List: The results of the request.
            Dict: The request metadata

        Resources:
            https://github.com/googleads/googleads-python-lib/blob/master/examples/ad_manager/v201808/report_service/run_ad_exchange_report.py#L31
            https://developers.google.com/ad-manager/api/adx_reporting_migration#metrics_columns
            https://developers.google.com/ad-manager/api/reference/v201802/ReportService.Column
        """

        # Run request and wait for the response
        data_downloader = self.client.GetDataDownloader(version)
        if self.verbose: print("Running query:", report_job)
        report_job_id = data_downloader.WaitForReport(report_job)

        # Save and convert the results
        #NOTE: converting the temp csv into a native python object so the library does not handle saving of files.
        filename = self._save_temp_file(data_downloader, report_job_id)
        return self._read_temp_file(filename) #results, column_names, meta_data

    def _save_temp_file(self, downloader, report_job_id):
        """ Create a temporary file of the results """

        #NOTE: I am not sure if this should convert to an object here and then delete the file or leave it.
        #NOTE: (cont) I will leave it like this for now while we debate if we should change it.
        report_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        downloader.DownloadReportToFile(report_job_id, 'CSV_DUMP', report_file, include_report_properties=True, use_gzip_compression=False)
        report_file.close()
        if self.verbose: print("File {} saved to {}".format(report_job_id, report_file.name))
        return report_file.name

    def _read_temp_file(self, filename):
        """ Convert the CSV of the results to native Python objects"""

        meta = {}
        cols = []
        data = []

        with open(filename) as file:
            reader = csv.reader(file, delimiter=',')
            for i, row in enumerate(reader):
                #NOTE: The report properties are in the first rows and are not the same length as the data.
                if 0 < i < 7:
                    meta[row[0]] = row[1]
                if i==8:
                    for col in row:
                        cols.append(col)
                #NOTE: I am not sure if this should be a list of lists and a separate list of indices.
                if i>8:
                    data.append(row)
        return data, cols, meta


if __name__ == '__main__':
    dfp = GoogleAdManager(verbose=True) # cred_file="C:\\BigQuery-422148a82d7c.json",

    # Sample Query
    query = ('SELECT BuyerAccountId, Name '
             'FROM Programmatic_Buyer '
             'ORDER BY BuyerAccountId ASC'
             )

    # Sample Report
    report_job = {
        'reportQuery': {
            'dimensions': ['AD_EXCHANGE_DATE','AD_EXCHANGE_PRODUCT_NAME', 'AD_EXCHANGE_PRICING_RULE_NAME', 'AD_EXCHANGE_TRANSACTION_TYPE'],
            'columns': ['AD_EXCHANGE_AD_REQUESTS', 'AD_EXCHANGE_IMPRESSIONS', 'AD_EXCHANGE_ESTIMATED_REVENUE'],
            'dateRangeType': 'LAST_WEEK',
            'timeZoneType': 'AD_EXCHANGE',
            'adxReportCurrency': 'USD'
        }
    }

    # dfp.run_pql(query)
    print(dfp.run_request(report_job))
