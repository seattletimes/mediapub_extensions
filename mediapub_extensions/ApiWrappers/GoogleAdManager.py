from googleads import ad_manager
from googleads import oauth2

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
        """
        data_downloader = self.client.GetDataDownloader(version)
        resp = data_downloader.DownloadPqlResultToList(query)
        return resp


if __name__ == '__main__':
    dfp = GoogleAdManager(verbose=True) # cred_file="C:\\BigQuery-422148a82d7c.json",
    # query = ('SELECT BuyerAccountId, Name '
    #          'FROM Programmatic_Buyer '
    #          'ORDER BY BuyerAccountId ASC'
    #          )
    # dfp.run_pql(query)
