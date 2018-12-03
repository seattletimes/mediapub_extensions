import pyodbc
import getpass
# import json
# import getpass
# import sys
#
class SQLServer():
    """
    Handles connections and queries to Microsoft SQL Server

    This class contains methods to connect to SQL Server and run
    queries on it.

    Requires:
        pyodbc: pip install pyodbc  https://github.com/mkleehammer/pyodbc

    Attributes:

    """

    verbose = False
    conn_string = None
    cursor = None


    def __init__(self, dsn=None, user_id=None, password=None, trusted_connection = False, verbose=True):
        """
        Create a SQL Server connection for this instance.

        Creates a SQL Server connection.

        Args:
            verbose (bool): Sets expressive output

        Yields:
            pyodbc.cursor: A pyodbc cursor object
        """
        self.verbose = verbose
        if self.verbose: print("initializing SQLServer")
        conn_string = self.__get_conn_string(dsn, user_id, password, trusted_connection)
        print(conn_string)
        self.conn_string = conn_string
        self.__set_cursor(conn_string)

    #####################################################
    # Connection Methods
    #####################################################

    def __set_cursor(self, conn_string):
        conn = pyodbc.connect(self.conn_string)
        self.cursor = conn.cursor()

    def __get_conn_string(self, dsn=None, user_id=None, password=None, trusted_connection = False):
        if dsn and user_id and password:
            return "DSN={};UID={};PWD={};Trusted_Connection={}".format(dsn, user_id, password, trusted_connection)
        else:
            dsn = input("DSN = ")
            uid = input("Username = ")
            password = getpass.getpass()
            return "DSN={};UID={};PWD={};Trusted_Connection={}".format(dsn, user_id, password, trusted_connection)

    #####################################################
    # Query Methods
    #####################################################

#     def run_query(self, SQL_CMD="SELECT current_version()", ignore_results=False):
#         """
#         Run a supplied query on Snowflake
#
#         This function will run a query that is passed to it on the Snowflake platform.
#
#         Example:
#             run_query(env=\"production\", SQL_CMD=\"SELECT * FROM table\")
#
#         Args:
#             env (str): Specifies if this query should run on staging or production.
#             SQL_CMD (str): The SQL command to be run
#
#         Returns:
#             list: A list of tuples containing the row level results of the query.
#
#         Raises:
#             SQL compilation error:
#         """
#
#         #NOTE: This does not have any checking on what queries are passed in and run.  Limits enforced by roles
#         cs = self.ctx.cursor()
#         try:
#             cs.execute(self.ROLE)
#             cs.execute(self.DB)
#             cs.execute(self.SCHEMA)
#             cs.execute(self.WAREHOUSE)
#             cs.execute(SQL_CMD)
#             if ignore_results: return True
#             results = cs.fetchall()
#             return results
#         finally:
#             cs.close()


if __name__=='__main__':
    sql = SQLServer("MSSQLAudre", "readonly", "pass")
