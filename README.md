### Project: Financial Report Generator Using Multi-Agent LLM Framework with Streamlit UI

### Overview:
This code is a multi-agent system designed to generate financial reports based on user-provided stock tickers. 
It uses Streamlit for a user-friendly interface, Autogen for orchestrating multiple AI agents, 
and built-in Python libraries for file handling, data validation, and reporting.

The system performs the following tasks:
1. **Input Processing**: Accepts user input (stock tickers or company names) through a Streamlit UI.
2. **Ticker Mapping**: Converts user input into valid stock tickers using a Ticker Mapping Agent.
3. **Data Retrieval**: 
   - Fetches stock prices, historical performance, and fundamental metrics using a Financial Assistant Agent.
   - Retrieves recent news headlines for each stock using a Research Assistant Agent.
4. **Report Generation**: 
   - Combines the retrieved data into an engaging financial report using a Writer Agent.
   - The report includes:
     - Stock performance analysis (e.g., normalized prices, fundamental ratios, correlations).
     - Market news headlines with insights.
     - A comparative table of stock metrics and possible future scenarios.
5. **Quality Assurance**:
   - Multiple Review Agents validate the content for:
     - Legal compliance.
     - Consistency in data and text alignment.
     - Completeness of required sections.
6. **Report Display**: The final report and relevant figures (e.g., normalized price graph) are displayed in the Streamlit interface.
7. **Fallback Handling**: Ensures proper error handling and fallback responses, such as missing images or invalid stock input.

### Key Components:
1. **Agents**: 
   - Financial Assistant: Fetches stock prices and metrics.
   - Research Assistant: Retrieves news headlines.
   - Writer: Generates the final financial report in markdown format.
   - Critic & Review Agents: Ensure quality by performing checks for consistency, legal compliance, completeness, and alignment.
   - Meta Reviewer: Aggregates all reviews for a final quality check.

2. **Streamlit Interface**:
   - Text Input: Users provide stock tickers or company names.
   - Button: Triggers analysis and report generation.
   - Report Display: Shows the generated financial report and any relevant images.

3. **Functions**:
   - get_ticker_from_agent(): Converts user input to valid stock tickers using the Ticker Mapping Agent.
   - autogen.initiate_chats(): Manages the multi-agent conversations and workflows.

4. **File Handling**:
   - The system checks for a generated image file (normalized_prices.png) and displays it if available.
   - If the image is missing, a fallback message is displayed.

5. **Error Handling**:
   - Handles invalid stock inputs, empty user inputs, and missing data gracefully.
   - Ensures no hallucinated or invalid data is included in the report.

### Code Flow:
1. **Input Collection**:
   - Users enter stock tickers through a text input box in Streamlit.
   - Input is split, cleaned, and sent to the Ticker Mapping Agent for validation.

2. **Agent Task Execution**:
   - Financial Assistant retrieves stock data and calculates key metrics.
   - Research Assistant gathers recent news headlines for the selected stocks.
   - Critic and Review Agents validate the content for accuracy, consistency, and completeness.
   - Writer Agent generates a markdown-based financial report.

3. **Data Presentation**:
   - The system checks for the normalized prices image file (normalized_prices.png) and displays it.
   - The financial report is displayed in markdown format within Streamlit.

4. **Termination**:
   - The agents reply with "TERMINATE" once the report is successfully completed and validated.

### Output:
- A comprehensive financial report that includes:
  - Stock performance analysis.
  - Fundamental metrics and comparisons.
  - News insights for each stock.
  - A table and figure for clarity.
- Clear error messages if inputs are invalid or data is unavailable.

### Usage:
Run this script in a Streamlit environment:
bash
streamlit run script_name.py

Have included docker file as well, if anyone wishes to run in production environment.

