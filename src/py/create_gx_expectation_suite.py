import sys
import warnings
from datetime import datetime
from time import time

import common
import great_expectations as gx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Set up logging
logger = common.get_logger()

# Create a GX context
context = gx.get_context()

# Suppress DeprecationWarning for create_expectation_suite
warnings.filterwarnings("ignore", category=DeprecationWarning)


def create_and_run_checkpoint(batch_request, expectation_suite_name):
    """Create a checkpoint, run validations, and build data documentation."""
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": expectation_suite_name,
            },
        ],
    )
    checkpoint_result = checkpoint.run()
    context.build_data_docs()

    return checkpoint_result


def save_expectation_suite(data_assistant_result, expectation_suite_name):
    """Save the expectation suite obtained from the data assistant."""
    try:
        expectation_suite = data_assistant_result.get_expectation_suite(expectation_suite_name=expectation_suite_name)
        context.add_or_update_expectation_suite(expectation_suite=expectation_suite)
        logger.info(f"\nExpectation suite '{expectation_suite_name}' saved successfully.\n")
    except Exception as e:
        logger.error(f"Error saving expectation suite: {e}")
        raise


def run_onboarding_data_assistant(batch_request, exclude_column_names=[]):
    """Run onboarding data assistant with the provided batch request and exclude column names."""
    try:
        data_assistant_result = context.assistants.onboarding.run(batch_request=batch_request)
        logger.debug("Data assistant run successful.")
        return data_assistant_result
    except Exception as e:
        logger.error(f"Error running data assistant: {e}")
        raise


def prepare_expectation_suite(input_table):
    """Prepare and create a new expectation suite with the current date as the name."""
    current_date_str = datetime.now().strftime("%Y%m%d")
    expectation_suite_name = f"{current_date_str}_{input_table}"

    try:
        context.create_expectation_suite(expectation_suite_name, overwrite_existing=True)
        logger.debug(f"GX expectation suite '{expectation_suite_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating expectation suite: {e}")
        raise

    return expectation_suite_name


def prepare_batch_request(input_table, gx_data_src_name, row_count_limit):
    """Prepare a batch request for the given data asset name."""
    my_asset = context.get_datasource(gx_data_src_name).get_asset(input_table)  # Retrieve data asset
    batch_request = my_asset.build_batch_request()  # build batch request

    batches = my_asset.get_batch_list_from_batch_request(batch_request)

    [logger.debug(batch.batch_spec) for batch in batches]

    return batch_request


def main():
    """Main function to execute the script."""
    try:
        input_tables, other_params = common.load_config_from_yaml()
        gx_data_src_name, row_count_limit = other_params["gx_data_src_name"], other_params["row_count_limit"]
        logger.debug(
            f"input tables = {input_tables}\ngx_data_src_name = {gx_data_src_name}\nrow_count_limit = {row_count_limit}"
        )

        table_times = []  # List to store elapsed time for each table

        for input_table in input_tables:
            logger.info(f"\nCreating (test) expectation suite for table: {input_table}")
            batch_request = prepare_batch_request(input_table, gx_data_src_name, row_count_limit)
            expectation_suite_name = prepare_expectation_suite(input_table)

            # Measure time taken by run_onboarding_data_assistant
            START_TIME = time()
            data_assistant_result = run_onboarding_data_assistant(batch_request)
            ELAPSED_TIME = int(round(time() - START_TIME, 0))

            # Store elapsed time and input table information in the list
            table_times.append({"table": input_table, "elapsed_time": ELAPSED_TIME})

            save_expectation_suite(data_assistant_result, expectation_suite_name)
            create_and_run_checkpoint(batch_request, expectation_suite_name)
        context.build_data_docs()

        logger.info("Time taken to create (test) expectation suite for tables:")
        # Log the elapsed time for each table after the for loop
        for table_info in table_times:
            logger.info(f"{table_info['table']}': {table_info['elapsed_time']} seconds.")

    except Exception as e:
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
