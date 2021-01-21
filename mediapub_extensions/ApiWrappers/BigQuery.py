import uuid
import time
import datetime
from google.cloud import bigquery
import google.cloud.bigquery.job
from google.cloud.bigquery.job import DestinationFormat
from google.cloud import storage
import os
import json

class BigQuery(object):
    """
    Handles connections and queries to Google BigQuery

    This class handles connections to Google BigQuery and allows queries to be run on it.

    Requires:
        google-api-python-client: pip install google-api-python-client
        google-cloud: pip install google-cloud==0.27.0

    Attributes:
        client (google.cloud.bigquery.Client): The BigQuery connection
        project (str): The Google Cloud project
        verbose (bool): The verbosity flag
    """
    client = None
    verbose = False
    project = None
    credentials = None

    # dataset = None
    # storageClient = None

    def __init__(self, cred_file, project, verbose=False):
        """
        Create a BigQuery connection

        Args:
            project (str): The Google Cloud project to connect to

        Yields:
            google.cloud.bigquery.Client: A BigQuery connection.
        """
        self.verbose = verbose
        self.project = project
        self.credentials = cred_file
        if self.verbose: print('initializing BigQuery client...')
        #NOTE: The Client only takes specific Google data formats, the from_service_account_json generates the proper format from a json file
        #NOTE: I am not sure if this project param does anything
        self.client = bigquery.Client.from_service_account_json(self.credentials, project=self.project)

    def run_query(self, query, use_legacy_sql=False, query_id=str(uuid.uuid4()), use_query_cache=True ,destination_dataset=None, destination_table=None, truncate=False):
        """
        Run a query

        Args:
            query (str): The query to be run
            use_legacy_sql (bool): Is the input query written using legacy sql
            query_id (str): The unique ID for the query
            use_query_cache (bool): Should the query use cached data when available
            destination_dataset (str): The dataset the destination_table should be saved to.
            destination_table (str): If the data should be saved to a flat table, name it here.
            truncate (bool): Should the destination_table be truncated before writing new rows.

        Returns:
            google.cloud.bigquery.table.RowIterator: The results of the query stored in an iterator
        """

        if destination_table is not None:
            write_disposition = (google.cloud.bigquery.job.WriteDisposition.WRITE_TRUNCATE) if truncate else (google.cloud.bigquery.job.WriteDisposition.WRITE_APPEND)
            table = destination_dataset + '.' + destination_table

            config = bigquery.QueryJobConfig(
                        # default_dataset=destination_dataset,
                        destination=table,
                        use_query_cache = use_query_cache,
                        use_legacy_sql = use_legacy_sql,
                        create_disposition = google.cloud.bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
                        write_disposition = write_disposition
                     )
        else:
            config = bigquery.QueryJobConfig(
                        use_query_cache = use_query_cache,
                        use_legacy_sql = use_legacy_sql
                     )

        job = self.client.query(query, job_config=config, job_id=query_id)
        return job.result()

    def process_results(self, results, as_dataframe=True, max_results=None):
        """
        Process the results from a QueryResults object

        Allows the results of a QueryResults object to be looped through and return the data

        Args:
            results (google.cloud.bigquery.query.QueryResults): The results of the query
            as_dataframe(bool): Should results be returned as a Pandas DataFrame or a Python Dict
            max_results (int): The maximum number of results to return on each page

        Returns:
            results: Dataframe unless as_dataframe==False otherwise dict
        """

        df = results.to_dataframe()
        df = df.head(max_results) if max_results else df
        if self.verbose: print("Processed " + str(df.shape[0]) + " results")
        return df if as_dataframe else df.to_dict('records')

    def export_table(self, project, dataset, table_id, bucket, filename, format="NEWLINE_DELIMITED_JSON", header_row=True, delimiter=','):
        """
        Saves a table to GCS

        Save the data from Google BigQuery to Google Cloud Storage (GCS)

        Args:
            project (str): The GCP Project name
            dataset (str): The name of the dataset containing the table in question
            table_id (str): The table name
            bucket (str): The GCS bucket location (i.e. folder)
            filename (str): The desired filename of the output files
            format (str): The format of the resulting file
            header_row (bool): Flag if a header row of column names should be exported
            delimiter (str): The delimiting character between columns

        Returns:
            job_id (str): The ID of the job
            result (str): The final state of the job
        """

        destination_url = "gs://{}/{}".format(bucket, filename)
        job_id = str(uuid.uuid4())
        table_ref = self.client.dataset(dataset, project=project).table(table_id)
        configs = bigquery.job.ExtractJobConfig(
                    destination_format = format,
                    print_header=header_row,
                    field_delimeter = delimiter
                  )
        if self.verbose: print("Starting load of {} to {} as {}".format(table_id, destination_url, job_id))
        extract_job = self.client.extract_table(table_ref, destination_url, job_id=job_id, job_config=configs)
        result = extract_job.result().state
        if self.verbose: print("Job {} is finished with a status of {}".format(job_id, result))

        return job_id, result


    def download_export(self, bucket, filename, destination_filename=None):
        if not destination_filename: destination_filename = filename
        storage_client = storage.Client.from_service_account_json(self.credentials, project=self.project)
        bucket = storage_client.get_bucket(bucket)
        bucket.blob(filename).download_to_filename(destination_filename)

    def get_gcs_files(self, bucket):
        storage_client = storage.Client.from_service_account_json(self.credentials, project=self.project)
        bucket = storage_client.get_bucket(bucket)
        return [b.name for b in bucket.list_blobs()]

    def delete_gcs_files(self, bucket, file):
        storage_client = storage.Client.from_service_account_json(self.credentials, project=self.project)
        bucket = storage_client.get_bucket(bucket)
        blob = bucket.blob(file)
        blob.delete()

    def delete_gcs_files_in_bucket(self, bucket):
        storage_client = storage.Client.from_service_account_json(self.credentials, project=self.project)
        bucket = storage_client.get_bucket(bucket)
        for b in bucket.list_blobs():
            blob = bucket.blob(b.name)
            blob.delete()

if __name__ == '__main__':
    print("Don't call directly.  Install package and import as a class.")

    cred_file = None
    project = 'fake-ga-project'
    query = 'SELECT fullVisitorId, visitId, date FROM `bigquery-public-data.google_analytics_sample.ga_sessions_20170801` LIMIT 10'
    dataset = 'api-tests'
    table = "api_test"
    bucket = 'api-tests'

    bq = BigQuery(cred_file=cred_file, project=project, verbose=True)
    results =bq.run_query(query, destination_dataset=project + '.' + dataset, destination_table=table, truncate=True)
    results = bq.process_results(results, max_results=3, as_dataframe=False, )
    print(results)
    bq.export_table(project, dataset, table, bucket, table + '.csv', format='CSV')
    print(bq.get_gcs_files(bucket))
