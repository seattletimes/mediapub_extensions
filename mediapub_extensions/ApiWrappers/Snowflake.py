import snowflake.connector as snowcon
import json
import getpass
import sys

class Snowflake():
    """
    Handles connections and queries to Snowflake Computing

    This class contains methods to connect to the Snowflake service and run
    queries on it.

    Requires:
        snowflake-connector-python: pip install snowflake-connector-python

    Attributes:
        user (str): The Snowflake username
        password (str): The Snowflake Password
        account (str): The Snowflake accountID
        ctx (snowflake.connector): The connection to Snowflake
    """

    user = None
    password = None
    account = None
    ctx = None

    def __init__(self, username=None, password=None, account=None, role='STAGE_R', db='ST_WEB', warehouse='ST_ANALYTICSAPI', schema='WEB_STAGE_META', verbose=False):
        """
        Create a Snowflake connection for this instance.

        Creates a Snowflake-Python connection.  If no username and
        password are passed, it will attempt other connection options (keyfile
        and command prompt)

        Args:
            username (str): The Snowflake Username
            password (str): The Snowflake Password

        Yields:
            snowflake.connector.connect: A Snowflake connection
        """

        self.verbose = verbose

        # First try passed in username and pass, then look for a keyfile, then ask the user
        if username is not None and password is not None and account is not None:
            self.set_creds_by_param(username, password, account)
        else:
            self.set_creds()
        self.set_environment_settings(role, db, warehouse, schema)
        if self.verbose: print("connecting to Snowflake...")
        self.ctx = snowcon.connect(user=self.user, password=self.password, account=self.account)

    #####################################################
    # Connection Methods
    #####################################################

    def set_creds(self):
        """ Get the Username and Password from the user """

        self.account = input("Snowflake Account = ")
        self.user = input("Snowflake UserName = ")
        self.password = getpass.getpass()

    def set_creds_by_param(self, username, passwd, account):
        """ Set the Username and Password from the Args """

        self.account = account
        self.user = username
        self.password = passwd

    def set_environment_settings(self, role='STAGE_R', db='ST_WEB', warehouse='ST_ANALYTICSAPI', schema='WEB_STAGE_META'):
        """
        Return settings to reach the Snowflake Enviornment

        Return SQL to set the settings that are used to reach
        Snowflake enviornments.  Currently, production and staging
        are the only enviornments in use.

        Args:
            env (str): The Snowflake enviornment settings to return

        Returns:
            role (str): SQL to set the correct Role.
            db (str): SQL to set the target database.
            warehouse (str): SQL to set the warehouse for data processing.
            schema (str): SQL to set the schema queries are run from.
        """

        self.ROLE = "USE ROLE {};".format(role)
        self.DB = "USE {};".format(db)
        self.WAREHOUSE = "USE WAREHOUSE {};".format(warehouse)
        self.SCHEMA = "USE SCHEMA {};".format(schema)

    def run_query(self, SQL_CMD="SELECT current_version()"):
        """
        Run a supplied query on Snowflake

        This function will run a query that is passed to it on the Snowflake platform.

        Example:
            run_query(env=\"production\", SQL_CMD=\"SELECT * FROM table\")

        Args:
            env (str): Specifies if this query should run on staging or production.
            SQL_CMD (str): The SQL command to be run

        Returns:
            list: A list of tuples containing the row level results of the query.

        Raises:
            SQL compilation error:
        """

        #NOTE: This does not have any checking on what queries are passed in and run.  Limits enforced by roles
        cs = self.ctx.cursor()
        try:
            cs.execute(self.ROLE)
            cs.execute(self.DB)
            cs.execute(self.SCHEMA)
            cs.execute(self.WAREHOUSE)
            cs.execute(SQL_CMD)
            results = cs.fetchall()
            return results
        finally:
            cs.close()

    ############################################################
    # Queries
    ############################################################

    def get_snowflake_version(self):
        """Return the Snowflake version number."""

        results = self.run_query()
        return results[0][0]


if __name__=='__main__':
    sf = Snowflake()
    sf.set_environment_settings("ETL_PULL", "ST_WEB", "ST_WEB_WH_PROD_ETL", "WEB_PROD")
    print(sf.get_snowflake_version())
