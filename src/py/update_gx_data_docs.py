import os
import re
import shutil
import sys
from datetime import datetime

import common
import great_expectations as gx
from bs4 import BeautifulSoup
from jinja2 import Environment
from jinja2 import FileSystemLoader

# Set up logging
logger = common.get_logger()
# logger = common.get_logger(log_level=logging.DEBUG)

# Create a GX context
context = gx.get_context()

# ---------------------
# Constants
# ---------------------
# filepath-specific
# ---------------------
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "src", "templates", "jinja_templates")
PYTHON_SCRIPTS_DIR = os.path.join(PROJECT_DIR, "src", "py")
# ---------------------
# Other
# ---------------------
GX_DATA_DOCS_DIR = "gx/uncommitted/data_docs/local_site/"
GX_DATA_DOCS_HTML_FILE = os.path.join(GX_DATA_DOCS_DIR, "index.html")
HTML_JINJA_TEMPLATE = os.path.join(TEMPLATES_DIR, "index.html.j2")
CURRENT_DATE_STR = datetime.now().strftime("%Y%m%d")


def create_backup(file_path):
    backup_path = os.path.join(GX_DATA_DOCS_DIR, "bkp_index.html")
    try:
        shutil.copyfile(file_path, backup_path)
        logger.debug(f"Backup created: {backup_path}")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")


def modify_html_file(file_path):
    """Modifies the specified HTML file content, replacing the specified text."""

    # Read the content of the HTML file
    with open(file_path) as file:
        content = file.read()

    # Define the pattern to be found using a regular expression
    old_text_pattern = r'<li class="nav-item">\s*<a\s*aria-controls="Expectation-Suites"\s*aria-selected="false"\s*class="nav-link"\s*data-toggle="tab"\s*href="#Expectation-Suites"\s*id="Expectation-Suites-tab"\s*role="tab">\s*Expectation Suites\s*</a>\s*</li>'  # noqa

    # Specify the text to be replaced and its replacement
    # old_text = (
    #     '<li class="nav-item">\n'
    #     '    <a class="nav-link" id="Expectation-Suites-tab" data-toggle="tab" href="#Expectation-Suites"\n'
    #     '      role="tab" aria-selected="false" aria-controls="Expectation-Suites">\n'
    #     "      Expectation Suites\n"
    #     "    </a>\n"
    #     "  </li>"
    # )

    # Define the replacement text
    new_text = (
        '<li class="nav-item">\n'
        '    <a class="nav-link" id="Expectation-Suites-tab" data-toggle="tab" href="#Expectation-Suites"\n'
        '      role="tab" aria-selected="false" aria-controls="Expectation-Suites">\n'
        "      Expectation Suites\n"
        "    </a>\n"
        "</li>"
        "\n"
        '<li class="nav-item">\n'
        '    <a class="nav-link" id="Profiling-Results-tab" data-toggle="tab" href="#Profiling-Results"\n'
        '      role="tab" aria-selected="false" aria-controls="Profiling-Results">\n'
        "      Profiling Results\n"
        "    </a>\n"
        "  </li>\n"
    )

    # Use re.search to check if the pattern exists in the content
    if re.search(old_text_pattern, content, re.DOTALL):
        # Use re.sub to replace the old text with the new text in the content
        modified_content = re.sub(old_text_pattern, new_text, content)

        # Write the modified content back to the file
        with open(file_path, "w") as file:
            file.write(modified_content)
        logger.debug(f"Text substitution successful in {file_path}")
    else:
        logger.error(f"No substitution made in {file_path}")
        sys.exit(1)


def add_data_profiling_content():
    try:
        input_tables, other_params = common.load_config_from_yaml()
        logger.debug(f"input tables = {input_tables}")

        jinja_template = setup_jinja_template("index.html.j2")
        template_path = os.path.join(TEMPLATES_DIR, "index.html.j2")

        # Validate the Jinja template
        if not os.path.exists(template_path):
            logger.error(f"Error: Jinja template '{jinja_template}' not found.")
            sys.exit(1)

        with open(GX_DATA_DOCS_HTML_FILE, "w") as op_file:
            op_file.write(jinja_template.render(input_tables=input_tables, current_data_str=CURRENT_DATE_STR))

    except Exception as e:
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


def setup_jinja_template(ip_jinja_template_file):
    """Set up/get the Jinja template"""
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    return jinja_env.get_template(ip_jinja_template_file)


def read_target_html_from_file(file_path):
    try:
        with open(file_path, encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.debug(f"ERROR: An error occurred while reading the input file: {e}")
        sys.exit(1)


def prettify_html(input_file):
    try:
        with open(input_file, encoding="utf-8") as file:
            html_content = file.read()

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Prettify the HTML content for formatting
        prettified_html = soup.prettify()

        # Save the prettified HTML content to a new file
        with open(input_file, "w", encoding="utf-8") as file:
            file.write(prettified_html)

        return prettified_html

    except Exception as e:
        logger.debug(f"ERROR: An error occurred while processing the input HTML: {e}")
        sys.exit(1)


def find_and_replace_html_code():
    try:
        # Prettify the HTML content and get the prettified HTML
        prettified_html = prettify_html(GX_DATA_DOCS_HTML_FILE)

        # -------------------------------------
        # String pattern declarations
        # -------------------------------------
        # HTML code pattern to find
        html_pattern = r"</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*<footer>\s*<p>\s*Stay current on everything GX with our newsletter"  # noqa

        # JavaScript code pattern to find
        js_pattern = r'\$\(document\)\.ready\(function\(\)\s*\{\s*\$\("#section-1-content-block-2-2-body-table"\)\.on\(\'click-row\.bs\.table\',\s*function\(e,\s*row,\s*\$element\)\s*\{\s*window\.location\s*=\s*\$element\.data\("href"\);\s*\}\)\s*}\s*\);\s*'  # noqa

        # Combined JavaScript/HTML code pattern
        combined_html_pattern = js_pattern + html_pattern

        # -------------------------------------
        # Pattern matching/check functions
        # -------------------------------------
        # Search for subsequent HTML content
        html_check_match = re.search(html_pattern, prettified_html, re.DOTALL)
        # Search for the specific JavaScript content
        js_match = re.search(js_pattern, prettified_html, re.DOTALL)
        # search for the above 2 variables combined
        combined_html_pattern_match = re.search(combined_html_pattern, prettified_html, re.DOTALL)

        # ----------------------------------------
        # Error handling for pattern matching
        # ----------------------------------------
        if html_check_match:
            logger.debug("SUCCESS: Subsequent HTML elements found in the file.")
        else:
            logger.error("ERROR: Subsequent HTML elements not found in the file.")
            sys.exit(1)

        if js_match:
            specific_js_code = js_match.group()
            logger.debug("SUCCESS: Specific JavaScript code found in the HTML file.")
            logger.debug(specific_js_code)
        else:
            logger.error("ERROR: Specific JavaScript content not found in the HTML file.")
            sys.exit(1)

        # Check if combined pattern is true
        if combined_html_pattern_match:
            logger.debug("SUCCESS: Combined JavaScript and HTML patterns found in the file.")

            # Read in the replacement HTML content (to replace the pattern) from a text file
            target_html = read_target_html_from_file(os.path.join(PYTHON_SCRIPTS_DIR, "txt/target_html.txt"))

            # Perform find and replace operation
            updated_html_file = re.sub(combined_html_pattern, target_html, prettified_html, flags=re.DOTALL)

            # we want to write 2 versions of the newly updated file out:
            # index.html & index.html.j2 - as we need this for jinja-rendering in the function 'add_data_profiling_content()'
            html_op_files = [GX_DATA_DOCS_HTML_FILE, HTML_JINJA_TEMPLATE]

            for html_file in html_op_files:
                try:
                    # Save the modified HTML content to the input file
                    with open(html_file, "w") as file:
                        file.write(updated_html_file)

                    # Parse the updated HTML content using BeautifulSoup for final consistent formatting
                    prettify_html(html_file)
                except Exception as e:
                    logger.error(f"Error occurred while writing {html_file}: {e}")
                    sys.exit(1)

            # Output success message
            logger.debug("SUCCESS: HTML processing and pattern replacement completed.")
        else:
            logger.error("ERROR: Combined JavaScript and HTML patterns not found in the file.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"ERROR: An error occurred during HTML processing and pattern replacement: {e}")
        sys.exit(1)


def main():
    try:
        # Check if the index.html file exists
        if os.path.exists(GX_DATA_DOCS_HTML_FILE):
            # Step 1: Create a backup of the original index.html file
            create_backup(GX_DATA_DOCS_HTML_FILE)

            # Step 2: Find and replace specific HTML and JavaScript patterns
            find_and_replace_html_code()

            # Step 3: Add data profiling content using Jinja templates
            add_data_profiling_content()

            # Step 4: Modify the HTML file content
            modify_html_file(GX_DATA_DOCS_HTML_FILE)

            # Step 5: Open the Great Expectations data documentation
            context.open_data_docs()
        else:
            # Log an error if the file doesn't exist
            logger.error(f"Error: File '{GX_DATA_DOCS_HTML_FILE}' not found.")
    except Exception as e:
        # Log any exceptions that occur during execution
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
