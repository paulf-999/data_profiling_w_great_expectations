import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from great_expectations.dataset.pandas_dataset import PandasDataset

# Load environment variables from .env file
load_dotenv()


def validate_inputs():
    """Validate the presence of required environment variables."""

    snowflake_env_vars = {}

    env_vars_to_validate = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
    ]

    for env_var in env_vars_to_validate:
        if not os.getenv(env_var):
            raise ValueError(f"{env_var} environment variable is not set.")
        else:
            snowflake_env_vars[env_var] = os.getenv(env_var)

    return snowflake_env_vars


def setup_snowflake_connection(snowflake_env_vars=validate_inputs()):
    snowflake_params = {
        "account": snowflake_env_vars["SNOWFLAKE_ACCOUNT"],
        "user": snowflake_env_vars["SNOWFLAKE_USER"],
        "password": snowflake_env_vars["SNOWFLAKE_PASSWORD"],
        "warehouse": snowflake_env_vars["SNOWFLAKE_WAREHOUSE"],
        "database": snowflake_env_vars["SNOWFLAKE_DATABASE"],
        "schema": snowflake_env_vars["SNOWFLAKE_SCHEMA"],
    }

    conn = snowflake.connector.connect(
        account=snowflake_params["account"],
        user=snowflake_params["user"],
        password=snowflake_params["password"],
        warehouse=snowflake_params["warehouse"],
        database=snowflake_params["database"],
        schema=snowflake_params["schema"],
    )

    return conn


def snowflake_query(conn, input_tbl, row_count_limit):
    sql_query = f"SELECT * FROM {input_tbl} LIMIT {row_count_limit};"
    snowflake_cursor = conn.cursor()
    snowflake_cursor.execute(sql_query)
    result = snowflake_cursor.fetchall()
    snowflake_cursor.close()
    conn.close()

    column_names = [desc[0] for desc in snowflake_cursor.description]
    df = pd.DataFrame(result, columns=column_names)

    pandas_dataset = PandasDataset(df)

    return pandas_dataset
