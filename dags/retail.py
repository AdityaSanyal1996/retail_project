from airflow.decorators import dag, task
from datetime import datetime
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator
from astro import sql as aql
from astro.files import File
from astro.sql.table import Table, Metadata
from astro.constants import FileType

@dag(
    start_date = datetime(2025, 1, 1),
    schedule = None, 
    catchup = False, 
    tags = ['retail'],
)
def retail():
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id = 'upload_csv_to_gcs',
        src = '/usr/local/airflow/include/dataset/Online_Retail.csv',
        dst = 'raw/online_retail.csv',
        bucket = 'online_retail_tutorial',
        gcp_conn_id = 'gcp',
        mime_type = 'text/csv',
    )

    create_retail_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id = 'create_retail_dataset',
        dataset_id = 'retail',
        gcp_conn_id = 'gcp',
    )

    gcs_to_raw = aql.load_file(
        task_id = 'gcs_to_raw',
        input_file = File(
            "gs://online_retail_tutorial/raw/online_retail.csv",
            conn_id = 'gcp',
            filetype = FileType.CSV,
        ),
        output_table = Table(
            name = 'raw_invoices',
            conn_id = 'gcp',
            metadata = Metadata(schema = 'retail')
        ),
        use_native_support = False,
    )

    @task.external_python(python = '/usr/local/airflow/soda_venv/bin/python')
    def check_load(scan_name='check_load', checks_subpath = 'sources'):
        from include.soda.check_function import check

        return check(scan_name, checks_subpath)

    check_load()
retail() 