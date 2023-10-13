# Bulk Data Profiling using Great Expectations

This repository provides a streamlined way to perform data profiling on a list of input tables using Great Expectations. Follow the instructions below to set up and run the data profiling process.

## Prerequisites

Before you begin, ensure you have the following in place:

1. **Configure `.env` File**

    <details>

    <summary>Expand for more details</summary>

    * Create the `.env` file by copying and renaming `.env_template`, e.g.:

        ```bash
        cp .env_template .env
        ```

    * Then populate the `.env` file, assigning values to the Snowflake vars listed below

        ```jinja
        # Snowflake credentials
        SNOWFLAKE_USER={{ SF_USER }}
        SNOWFLAKE_PASSWORD={{ SF_PASSWORD }}
        SNOWFLAKE_ACCOUNT={{ SF_ACCOUNT }}
        SNOWFLAKE_REGION={{ SF_REGION }}
        SNOWFLAKE_ROLE={{ SF_ROLE }}
        SNOWFLAKE_WAREHOUSE={{ SF_WAREHOUSE }}
        SNOWFLAKE_DATABASE={{ SF_DATABASE }}
        SNOWFLAKE_SCHEMA={{ SF_SCHEMA }}
        SNOWFLAKE_HOST={{ SF_HOST }}
        INPUT_TABLE={{ SF_EG_TABLE }}
        GX_DATA_SRC={{ GX_SOURCE_NAME }}
        ROW_COUNT_LIMIT=30
        ```

    </details>

2. **Enter list of input tables in `config.yaml`**

    <details>

    <summary>Expand for more details</summary>

    * Open `config.yaml`.
    * Under the `input_tables` key, list the tables you want to profile, e.g.:

    ```yaml
    input_tables:
        - table_name_1
        - table_name_2
        # Add more input tables as needed
    ```

    </details>

## Usage

After meeting the above prerequisites, profile your input tables using the following command:

```shell
make all
```

This command will:

1. Create a Python Virtual Environment with the required Python libraries
    * See Makefile target `deps`.
2. Create a Great Expectations (GX) project with the list of Snowflake tables you provided
    * See Makefile target `install`.
3. Create a data profile and (test) expectation suite, per-input table
    * See Makefile target `create_gx_profiler_and_expectation_suite`.
4. Generate GX 'data docs' - i.e., HTML pages to view the content.
    * See Makefile target `update_gx_data_docs`.

Feel free to reach out if you encounter any issues or have questions about the process. Happy data profiling!
