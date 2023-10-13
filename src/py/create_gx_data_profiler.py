import logging
import os
import sys
import warnings
from datetime import datetime

import common
import snowflake_client
from great_expectations.profile.basic_dataset_profiler import BasicDatasetProfiler
from great_expectations.render.renderer import ExpectationSuitePageRenderer
from great_expectations.render.renderer import ProfilingResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView

# Set up logging
logger = common.get_logger(log_level=logging.INFO)


# Suppress DeprecationWarning for create_expectation_suite
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


def remove_relative_paths_from_html(html_file_path):
    """Removes occurrences of the string '../../../../' from the html file."""

    # Read the content of the HTML file and modify it
    with open(html_file_path) as file:
        content = file.read()
        modified_content = content.replace("../../../../", "../")

    # Write the modified content back to the HTML file
    with open(html_file_path, "w") as file:
        file.write(modified_content)


def write_html_file(directory, filename, content):
    """Write HTML content to a file in the specified directory"""
    with open(os.path.join(directory, filename), "w") as file:
        file.write(content)


def create_directory(directory):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"Directory created: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")


def generate_data_profiling_html(pandas_dataset, input_table):
    # Run the basic profiler
    expectation_suite_based_on_profiling, validation_result_based_on_profiling = pandas_dataset.profile(
        BasicDatasetProfiler
    )

    # Render html content for profiling and expectation suite
    profiling_result_html = DefaultJinjaPageView().render(
        ProfilingResultsPageRenderer().render(validation_result_based_on_profiling)
    )
    expectation_based_on_profiling_html = DefaultJinjaPageView().render(
        ExpectationSuitePageRenderer().render(expectation_suite_based_on_profiling)
    )

    DATA_DOCS_DIR = "gx/uncommitted/data_docs/local_site/"
    PROFILING_RESULTS_DIR = os.path.join(DATA_DOCS_DIR, "profiling_results")
    EXPECTATION_SUITE_DIR = os.path.join(DATA_DOCS_DIR, "expectation_suite")
    CURRENT_DATE_STR = datetime.now().strftime("%Y%m%d")

    # Define file information as tuples (directory, filename, content)
    files_to_process = [
        (PROFILING_RESULTS_DIR, f"{CURRENT_DATE_STR}_{input_table}.html", profiling_result_html),
        (EXPECTATION_SUITE_DIR, f"{CURRENT_DATE_STR}_{input_table}.html", expectation_based_on_profiling_html),
    ]

    # loop through 'files_to_process' to call the same functions below on each
    for directory, filename, content in files_to_process:
        create_directory(directory)  # Create directories if they don't exist
        write_html_file(directory, filename, content)  # Write HTML content to files
        remove_relative_paths_from_html(os.path.join(directory, filename))  # Remove relative file paths

    logger.info(f"Created data profile for table: {input_table}")

    return


def main():
    try:
        input_tables, other_params = common.load_config_from_yaml()
        gx_data_src_name, row_count_limit = other_params["gx_data_src_name"], other_params["row_count_limit"]
        logger.debug(
            f"input tables = {input_tables}\ngx_data_src_name = {gx_data_src_name}\nrow_count_limit = {row_count_limit}"
        )

        for input_table in input_tables:
            logger.debug(f"Input table = {input_table}")

            pandas_dataset = snowflake_client.snowflake_query(
                snowflake_client.setup_snowflake_connection(), input_table, row_count_limit
            )
            generate_data_profiling_html(pandas_dataset, input_table)
    except Exception as e:
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
