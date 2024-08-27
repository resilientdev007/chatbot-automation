# LLM-based Chatbot Automation Framework

This framework automates interactions with the Mistral chatbot, validating responses against expected answers. It's designed for developers and testers who want to ensure the chatbot's accuracy and reliability.

## Prerequisites

- Python 3.12.4 or higher
- Docker (optional)

## Installation
1. **Clone the repository**:
   ```sh
   git clone https://github.com/your-username/chatbot-automation.git
   
   cd chatbot-automation

2. **Set up Python Virtual Environment (Optional but highly recommended)**
    ```
    python -m venv myenv
    activate venv

3. **Install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm

4. **Install Playwright and the necessary browser:**
    ```python
    pip install playwright
    playwright install

    
5. **Set up environment variables for the chatbot (Mistral Bot) credentials**:
     ```sh
    export CHATBOT_USERNAME=your_username
    export CHATBOT_PASSWORD=your_password

    set CHATBOT_USERNAME=your_username
    set CHATBOT_PASSWORD=your_password

## Usage

Ensure that the Excel sheet with questions and expected answers is placed in the data directory named as questions.xlsx.

1. **Run the main script**:
    ```sh
    cd scripts
    python main.py

## Docker Setup (Optional)

1. **Build the Docker image**:
    ```sh
    docker build -t chatbot-automation .

2. **Run the Docker container**:
    ```sh
    docker run -e CHATBOT_USERNAME=your_username -e CHATBOT_PASSWORD=your_password -v $(pwd)/reports:/app/reports chatbot-automation

## Configuration

The framework allows customization through a configuration file located in the `config` directory. This file includes settings for similarity thresholds and weights for different validation metrics.

### Steps to modify:
1. Navigate to `config/config.yaml`.
2. Adjust the thresholds and weights according to your testing needs.
3. Save the file.

    **Example configuration file (`config.yaml`):**

    ```yaml
    THRESHOLDS = {
        'similarity_score': 0.75,
        'keyword_match': 0.3,
        'fuzzy_score': 70,
        'levenshtein_similarity': 0.8,
    }

    WEIGHTS = {
        'similarity_score': 1,
        'keyword_match': 1,
        'fuzzy_match': 1,
        'levenshtein_similarity': 1,
    }

## Data Directory

The `data` directory is where you store the Excel file containing questions and expected answers. Ensure that this file is named `questions.xlsx` before running the script.

**Expected Excel File Structure:**
- Column 1: `Question`
- Column 2: `Expected Answer`
- Column 3: `Expected Data`


## Contact
For any questions or issues, please contact tarun.khosla@nagarro.com


