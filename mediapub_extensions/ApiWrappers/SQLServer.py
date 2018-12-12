import pyodbc
import getpass

class SQLServer():
    """
    Handles connections and queries to Microsoft SQL Server

    This class contains methods to connect to SQL Server and run
    queries on it.

    Requires:
        pyodbc: pip install pyodbc  https://github.com/mkleehammer/pyodbc
        odbc driver: https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017
        dsn (optional): https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Windows , https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-SQL-Server-from-Linux-or-Mac

    Attributes:
        conn_string (str): The SQL Server connection string
        cursor (pyodbc.cursor): The ODBC cursor https://docs.microsoft.com/en-us/sql/odbc/reference/develop-app/cursors?view=sql-server-2017
        verbose (bool): The verbosity flag

    Resources:
        https://github.com/mkleehammer/pyodbc/issues/276
    """

    verbose = False
    conn_string = None
    cursor = None
    conn = None


    def __init__(self, dsn=None, driver=None, server=None, db=None, user_id=None, password=None, trusted_connection = False, verbose=False):
        """
        Create a SQL Server connection for this instance.

        Creates a SQL Server connection.

        Args:
            verbose (bool): Sets expressive output

        Yields:
            pyodbc.cursor: A pyodbc cursor object
        """

        self.verbose = verbose
        if self.verbose: print("initializing SQL Server...")
        self.conn_string = self.__get_conn_string(dsn, driver, server, db, user_id, password, trusted_connection)
        self.__set_cursor(self.conn_string)
        if self.verbose: print("SQL Server connection established")

    #####################################################
    # Connection Methods
    #####################################################

    def __set_cursor(self, conn_string):
        """ Connect to the server and get a cursor """

        self.conn = pyodbc.connect(conn_string)
        self.cursor = self.conn.cursor()

    def __get_conn_string(self, dsn=None, driver=None, server=None, db=None, user_id=None, password=None, trusted_connection = False):
        """ Build the auth connection string """

        #TODO: This should handle more auth configs, e.g. trusted_connection with no password, etc
        trusted_connection = "Yes" if trusted_connection else "No" # trusted_connection takes Yes/No instead of True/False
        if dsn and user_id and password:
            return "DSN={};UID={};PWD={};Trusted_Connection={}".format(dsn, user_id, password, trusted_connection)
        if driver and server and user_id and password:
            return "DRIVER={{{}}};SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection={}".format(driver, server, db, user_id, password, trusted_connection)
        else:
            driver = input("Driver = ")
            server = input("Server = ")
            db = input("Database = ")
            uid = input("Username = ")
            password = getpass.getpass()
            return "DRIVER={};SERVER={};DATABASE={};UID={};PWD={};Trusted_Connection={}".format(driver, server, db, uid, password, trusted_connection)

    #####################################################
    # Query Methods
    #####################################################

    def run_query(self, query, results=True):
        """
        Run a SQL query and optionally return the results

        Execute the provided SQL Query and return the results

        Args:
            query (str): The SQL Query to be run

        Returns:

        """

        #NOTE: This should probably return standard python objects intead of pyodbc.Row
        #TODO: This should get some injection checking.  For now assuming good faith actors
        query = self.cursor.execute(query)
        if results:
            return self.cursor.fetchall()
        else:
            return True

    def commit(self):
        return self.conn.commit()

    def get_cols(self):
        """ Get the column names as a list """
        return [column[0] for column in self.cursor.description]


if __name__=='__main__':
    # print(pyodbc.drivers()) # Run to see a list of installed drivers
    sql = SQLServer()
    query = 'SELECT * FROM [AUDREPMETA].[reporting].[starts]'
    results = sql.run_query(query)
    cols = sql.get_cols()
    print(cols)
    print(type(results[0]), " - ", results[0])
