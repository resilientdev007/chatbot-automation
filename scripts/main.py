import time
import pandas as pd
import asyncio
import logging
import os
import yaml
from playwright.async_api import async_playwright
from validation import validate_response, validate_expected_data, generate_report

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the configuration from the config.yaml file
# config_path = os.path.join('../config', 'config.yaml')
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'config', 'config.yaml')


# Set headless mode from environment variable, default to False
headless_mode = os.getenv('HEADLESS_MODE', 'False').lower() in ['true', '1', 'yes']

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

async def _login(page, username, password):
    """
    Logs into the chatbot using the provided username and password.

    Args:
        page (Page): The Playwright page object.
        username (str): The username for login.
        password (str): The password for login.

    Raises:
        Exception: If login fails or any error occurs during the login process.
    """
    try:
        # Locate login form elements
        login_form = page.locator("[data-testid='login-flow']")
        username_field = login_form.locator("input[name='identifier']")
        password_field = login_form.locator("input[name='password']")
        submit_button = login_form.locator("button[type='submit']")

        # Input credentials
        await username_field.fill(username)
        await password_field.fill(password)

        # Submit login form
        await submit_button.click()

        try:
            # Wait for successful login
            await page.wait_for_selector('textarea[placeholder="Ask anything!"]', timeout=5000)
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise

async def _interact_with_chatbot(page, question):
    """
    Interacts with the chatbot by sending a question and retrieving the response.

    Args:
        page (Page): The Playwright page object.
        question (str): The question to ask the chatbot.

    Returns:
        str: The response text from the chatbot.

    Raises:
        Exception: If any error occurs during the interaction with the chatbot.
    """
    try:
        # Find the input field and send the question
        await page.wait_for_selector('textarea[placeholder="Ask anything!"]')
        input_field = page.locator('textarea[placeholder="Ask anything!"]')
        await input_field.fill(question)
        await input_field.press("Enter")
        
        time.sleep(15)

        # Wait for up to 20 seconds for the response to appear
        await page.wait_for_selector("div.prose p, div.prose li", timeout=20000)

        # Locate all <p> and <li> elements within the last div with class 'prose'
        prose_div = page.locator("div.prose").last
        all_response_elements = await prose_div.locator("p, li").all()

        if all_response_elements:
            # Combine the text of all elements into a single response
            combined_text = "\n".join([await element.inner_text() for element in all_response_elements])
        else:
            combined_text = "No response found"

        logging.info(f"Question: {question}")
        logging.info(f"Response: {combined_text}")

        return combined_text
    except Exception as e:
        logging.error(f"Error interacting with chatbot: {e}")
        raise

def _write_results(file_path, data, sheet_name):
    """
    Writes the results to an Excel file.

    Args:
        file_path (str): The path to the Excel file.
        data (list of dict): The data to write to the Excel file.
        sheet_name (str): The name of the sheet in the Excel file.

    Raises:
        Exception: If any error occurs during the writing process.
    """
    try:
        # Create a DataFrame from the results
        df = pd.DataFrame(data, columns=['Question', 'Actual Answer', 'Expected Answer', 'Similarity Score', 'Keyword Match', 'Fuzzy Score', 'Fuzzy Match', 'Expected Data Match', 'Levenshtein Similarity', 'Combined Score'])
        # Write the DataFrame to an Excel file
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        logging.error(f"Error writing results to file: {e}")
        raise

async def main():
    """
    Main function to read questions, interact with the chatbot, validate responses, and write results.

    Raises:
        Exception: If any error occurs during the execution of the main function.
    """
    try:
         # Get credentials from environment variables
        username = os.getenv('CHATBOT_USERNAME')
        password = os.getenv('CHATBOT_PASSWORD')

        if not username or not password:
            logging.error("Username and password must be set in environment variables")
            print("Error: Username and password must be set in environment variables")
            return
        
        # Read questions from Excel
        questions_df = pd.read_excel("../data/questions.xlsx")
        questions = questions_df["Question"].tolist()
        expected_answers = questions_df["Expected Answer"].tolist()
        expected_data = questions_df["Expected Data"].tolist()

        results = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            page = await browser.new_page()
            await page.goto("https://chat.mistral.ai/chat")

            # Login to the chatbot
            await _login(page, username, password)

            for question, expected_answer, expected_data_item in zip(questions, expected_answers, expected_data):
                response_text = await _interact_with_chatbot(page, question)

                # Validate the response
                similarity_score, keyword_match, fuzzy_score, fuzzy_match, levenshtein_similarity, combined_score = validate_response(expected_answer, response_text, config=config)
                expected_data_match = validate_expected_data(expected_data_item, response_text)

                results.append({
                    'Question': question,
                    'Actual Answer': response_text,
                    'Expected Answer': expected_answer,
                    'Similarity Score': similarity_score,
                    'Keyword Match': keyword_match,
                    'Fuzzy Score': fuzzy_score,
                    'Fuzzy Match': fuzzy_match,
                    'Levenshtein Similarity': levenshtein_similarity,
                    'Combined Score': combined_score,
                    'Expected Data Match': expected_data_match
                })

            await browser.close()

        # Convert results to DataFrame and print or save
        results_df = pd.DataFrame(results)
        _write_results('../reports/reports.xlsx', results, sheet_name='Score')
        generate_report(results_df, output_path='../reports/reports.xlsx', sheet_name='Metrics')
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")