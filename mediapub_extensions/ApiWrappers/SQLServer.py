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
#     user = None
#     password = None
#     account = None
#     ctx = None
#
    def __init__(self, dsn, user_id, password, trusted_connection = False, verbose=True):
         # , username=None, password=None, account=None,  verbose=False):
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
        conn_string = "DSN={};UID={};PWD={};Trusted_Connection={}".format(dsn, user_id, password, trusted_connection)
        print(conn_string)
#         self.verbose = verbose
#
#         # First try passed in username and pass, then look for a keyfile, then ask the user
#         if username is not None and password is not None and account is not None:
#             self.set_creds_by_param(username, password, account)
#         else:
#             self.set_creds()
#         self.set_environment_settings(role, db, warehouse, schema)
#         if self.verbose: print("connecting to Snowflake...")
#         self.ctx = snowcon.connect(user=self.user, password=self.password, account=self.account)
#
#     #####################################################
#     # Connection Methods
#     #####################################################
#
#     def set_creds(self):
#         """ Get the Username and Password from the user """
#
#         self.account = input("Snowflake Account = ")
#         self.user = input("Snowflake UserName = ")
#         self.password = getpass.getpass()
#
#     def set_creds_by_param(self, username, passwd, account):
#         """ Set the Username and Password from the Args """
#
#         self.account = account
#         self.user = username
#         self.password = passwd
#
#     def set_environment_settings(self, role='STAGE_R', db='ST_WEB', warehouse='ST_ANALYTICSAPI', schema='WEB_STAGE_META'):
#         """
#         Return settings to reach the Snowflake Enviornment
#
#         Return SQL to set the settings that are used to reach
#         Snowflake enviornments.  Currently, production and staging
#         are the only enviornments in use.
#
#         Args:
#             env (str): The Snowflake enviornment settings to return
#
#         Returns:
#             role (str): SQL to set the correct Role.
#             db (str): SQL to set the target database.
#             warehouse (str): SQL to set the warehouse for data processing.
#             schema (str): SQL to set the schema queries are run from.
#         """
#
#         self.ROLE = "USE ROLE {};".format(role)
#         self.DB = "USE {};".format(db)
#         self.WAREHOUSE = "USE WAREHOUSE {};".format(warehouse)
#         self.SCHEMA = "USE SCHEMA {};".format(schema)
#
#     #####################################################
#     # Query Methods
#     #####################################################
#
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
#
#     def push_files(self, PATH, stage):
#         SQL_PUT = "put file://" + PATH + " @S_" + stage + " auto_compress=true;"
#         return self.run_query(SQL_PUT, ignore_results=True)
#         pass
#
#     def process_files(self, table, stage, format, on_error="SKIP_FILE", purge=True):
#         SQL_COPY = "copy into " + table + " "\
#                 "from @S_" + stage + " "\
#                 "file_format = (format_name = " + format + ") "\
#                 "ON_ERROR = " + on_error + " "\
#                 "PURGE = " + purge + ";"
#         return self.run_query(SQL_COPY, ignore_results=True)
#
#     ############################################################
#     # Queries
#     ############################################################
#
#     def get_snowflake_version(self):
#         """Return the Snowflake version number."""
#
#         results = self.run_query()
#         return results[0][0]
#
#
if __name__=='__main__':
    sql = SQLServer("MSSQLAudre", "readonly", "pass")
