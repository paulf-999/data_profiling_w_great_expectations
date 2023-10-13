import logging
import sys
import warnings

import common
import great_expectations as gx

# Set up logging
logger = common.get_logger(log_level=logging.INFO)

# Suppress DeprecationWarning for create_expectation_suite
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_or_create_datasource(context, gx_data_src_name):
    """Get an existing datasource or create a new one if not exists."""
    try:
        # Attempt to get an existing datasource with the given name
        return context.get_datasource(gx_data_src_name)
    except ValueError:
        # If the datasource doesn't exist, create a new one with the provided name
        return context.sources.add_snowflake(
            name=gx_data_src_name, connection_string=common.create_snowflake_connection_string()
        )


def add_snowflake_tables_to_gx():
    """Load configuration and add assets to the Great Expectations data context."""
    try:
        # Validate environment variables
        common.validate_environment_variables()

        # Set up a data context
        context = gx.data_context.DataContext()

        # Fetch input parameters from config.yaml
        input_tables, other_params = common.load_config_from_yaml()

        # Fetch the remaining params
        gx_data_src_name, row_count_limit = other_params["gx_data_src_name"], other_params["row_count_limit"]

        # Get or create datasource and add assets
        for table in input_tables:
            try:
                datasource = get_or_create_datasource(context, gx_data_src_name)
                # Add table as a query asset with row_count_limit
                datasource.add_query_asset(name=table, query=f"SELECT * FROM {table} LIMIT {row_count_limit}")
                logger.debug(f"Table '{table}' added successfully.")
            except Exception as e:
                logger.error(f"Error adding table '{table}': {e}")
                raise
    except (common.MissingEnvironmentVariableError, ValueError) as e:
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Load and add assets to the Great Expectations data context
    add_snowflake_tables_to_gx()
