# Import necessary libraries
import os  # For checking file existence
import re  # For splitting input strings using delimiters
import autogen  # A multi-agent framework to coordinate LLM agents
import streamlit as st  # For building the user interface (UI)
from datetime import datetime  # For fetching the current date

# Configure the LLM (Language Model) for all agents
llm_config = {
    "model": "gpt-4o-mini",  # Model type to use for tasks
    "api_key": "sk-proj-fakeid-replace-this-with-your-own-key"  # API key placeholder (replace with a valid key)
}

# The writing task defines a structured financial report template
writing_tasks = [
        """Develop an engaging financial report using all information provided, include the normalized_prices.png figure,
        and other figures if provided.
        Mainly rely on the information provided. 
        Create a table containing current prices and comparing all the fundamental ratios and data.
        Provide comments and description of all the fundamental ratios and data.
        Compare the stocks, consider their correlation and risks, provide a comparative analysis of the stocks.
        Provide a summary of the recent news about each stock. 
        Ensure that you comment and summarize the news headlines for each stock, provide a comprehensive analysis of the news.
        Provide connections between the news headlines provided and the fundamental ratios.
        Provide an analysis of possible future scenarios. 
        """]


# ------------------ Agent Definitions ------------------ #
# 2 separate agents are used initially one financial assistant and another research assistant

# Financial Assistant: Fetches financial data and metrics for selected stocks
financial_assistant = autogen.AssistantAgent(
    name="Financial_assistant",
    llm_config=llm_config,
)

# Research Assistant: Gathers news headlines related to the stocks
research_assistant = autogen.AssistantAgent(
    name="Researcher",
    llm_config=llm_config,
)

# Writer: Generates a markdown-based financial report
writer = autogen.AssistantAgent(
    name="writer",
    llm_config=llm_config,
    system_message="""
        You are a professional writer, known for
        your insightful and engaging finance reports.
        You transform complex concepts into compelling narratives. 
        Include all metrics provided to you as context in your analysis.
        Only answer with the financial report written in markdown directly, do not include a markdown language block indicator.
        Only return your final work without additional comments like commenting on the analysis.
        """,
)

# Define an agent for exporting tasks (currently unused in this workflow, 
# but reserved for future tasks such as exporting finalized reports or analysis files).
export_assistant = autogen.AssistantAgent(
    name="Exporter",
    llm_config=llm_config,
)
# ===

# Critic: Reviews the generated report and ensures high quality
#Each of the agents below till meta agent have been defined to perform a narrow, defined task.
critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content.",
)

legal_reviewer = autogen.AssistantAgent(
    name="Legal Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer, known for "
        "your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

consistency_reviewer = autogen.AssistantAgent(
    name="Consistency_reviewer",
    llm_config=llm_config,
    system_message="You are a consistency reviewer, known for "
        "your ability to ensure that the written content is consistent throughout the report. "
        "Refer numbers and data in the report to determine which version should be chosen " 
        "in case of contradictions. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

textalignment_reviewer = autogen.AssistantAgent(
    name="Text _lignment_reviewer",
    llm_config=llm_config,
    system_message="You are a text data alignment reviewer, known for "
        "your ability to ensure that the meaning of the written content is aligned "
        "with the numbers written in the text. " 
        "You must ensure that the text clearely describes the numbers provided in the text "
        "without contradictions. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

completion_reviewer = autogen.AssistantAgent(
    name="Completion_Reviewer",
    llm_config=llm_config,
    system_message="You are a content completion reviewer, known for "
        "your ability to check that financial reports contain all the required elements. "
        "You always verify that the report contains: a news report about each asset, " 
        "a description of the different ratios and prices, "
        "a description of possible future scenarios, a table comparing current data and fundamental ratios and "
        " at least a single figure. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

meta_reviewer = autogen.AssistantAgent(
    name="Meta_Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggregate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

# ---------------------- Helper Function: Reflection Message ---------------------- #
def reflection_message(recipient, messages, sender, config):
    """
    Constructs a review message for agents involved in the review process.
    
    Parameters:
        recipient (autogen.AssistantAgent): The agent receiving the review task.
        messages (list): Not used in this context but available for future extensions.
        sender (autogen.AssistantAgent): The agent whose work is being reviewed.
        config (dict): Optional configurations for the function (not used in this case).
    
    Returns:
        str: A formatted string containing the last message content from the sender agent
             for the recipient to review.
    """
    # Fetch the last message sent by the sender agent to be reviewed by the recipient
    return f'''Review the following content. 
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

# ---------------------- Review Workflows Definition ---------------------- #
# List of review tasks where each agent analyzes the output from the 'writer' agent
# and provides specific feedback. The 'meta_reviewer' aggregates all feedback at the end.
review_chats = [
    {
        "recipient": legal_reviewer,  # Agent that checks for legal compliance
        "message": reflection_message,  # The helper function provides the review content
        "summary_method": "reflection_with_llm",  # LLM-based summarization method
        "summary_args": {
            "summary_prompt": 
                "Return review into a JSON object only:"
                "{'Reviewer': '', 'Review': ''}.",  # Enforce structured JSON output
        },
        "max_turns": 1  # Restrict the agent to one turn of feedback
    },
    {
        "recipient": textalignment_reviewer,  # Agent that checks alignment between text and data
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": 
                "Return review into a JSON object only:"
                "{'reviewer': '', 'review': ''}",  # Consistent JSON format
        },
        "max_turns": 1
    },
    {
        "recipient": consistency_reviewer,  # Agent that checks for internal consistency
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": 
                "Return review into a JSON object only:"
                "{'reviewer': '', 'review': ''}",  # Enforce JSON output
        },
        "max_turns": 1
    },
    {
        "recipient": completion_reviewer,  # Agent that checks report completeness
        "message": reflection_message, 
        "summary_method": "reflection_with_llm",
        "summary_args": {
            "summary_prompt": 
                "Return review into a JSON object only:"
                "{'reviewer': '', 'review': ''}",  # Structured feedback format
        },
        "max_turns": 1
    },
    {
        "recipient": meta_reviewer,  # Aggregator agent for all reviewer feedback
        "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.", 
        "max_turns": 1  # Single-turn task to finalize consolidated feedback
    },
]

# ---------------------- Register Nested Chats ---------------------- #
# The Critic agent orchestrates nested reviews by passing the 'writer' output
# to the different reviewers defined in 'review_chats'.
critic.register_nested_chats(
    review_chats,  # List of reviewers and their tasks
    trigger=writer,  # 'writer' agent acts as the trigger for the review process
)

# ===
# User Proxy Agent: Executes code in a local directory
user_proxy_auto = autogen.UserProxyAgent(
    name="User_Proxy_Auto",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "coding",
        "use_docker": False,
    },  
)


# This agent tries to interpret the user input as a company name and returns its ticker directly.
ticker_mapping_agent = autogen.AssistantAgent(
    name="TickerMappingAgent",
    llm_config=llm_config,
    system_message="""
    You are a ticker mapping agent. The user will provide a term related to a company or asset.
    Your job is to interpret the user's input as a recognized publicly traded company or a known traded asset, find its ticker and return it.
    If you can clearly identify which company/asset it refers to, return the recognized company's ticker.
    If you are not sure, return 'UNKNOWN'.
    For example, if user says 'alphabet inc' or 'google drive', understand it refers to Alphabet Inc (Google) and return GOOGL.
    If user says 'Bit coin', understand it might refer to Bitcoin and return BTC.
    Return only the ticker and nothing else
    If completely unsure, return 'UNKNOWN'.
    """
)


def get_ticker_from_agent(user_input: str):
    # Initiate a single chat round with the ticker_mapping_agent.
    response = autogen.initiate_chats(
        [
            {
                "sender": user_proxy_auto,
                "recipient": ticker_mapping_agent,
                "message": f"The user typed: '{user_input}'. Identify the ticker.",
                "carryover": "",
                "max_turns": 1,
                "summary_method": None
            }
        ]
    )
    ticker = response[-1].chat_history[-1]["content"].strip().upper()
    return ticker


assets = st.text_input("Assets you want to analyze (provide the tickers)?")
hit_button = st.button('Start analysis')

if hit_button:
    raw_input = assets.strip()
    if not raw_input:
        st.error("No stock input provided.")
        st.stop()

    # Split on commas, semicolons, or spaces
    potential_stocks = re.split(r"[,; ]+", raw_input)
    potential_stocks = [x for x in potential_stocks if x]

    final_stocks = []
    # For each input, call the ticker_mapping_agent using the helper function
    for item in potential_stocks:
        ticker = get_ticker_from_agent(item)
        if ticker != "UNKNOWN":
            final_stocks.append(ticker)

    # Limit to 5 stocks
    if len(final_stocks) > 4:
        st.warning("Only 4 stocks allowed at once. App by default will take the first 4 inputs.")
        final_stocks = final_stocks[:5]

    # If no valid tickers detected
    if not final_stocks:
        st.error("No such stock exists.")
        st.stop()

    date_str = datetime.now().strftime("%Y-%m-%d")

    financial_tasks = [
        f"""Today is the {date_str}. 
        What are the current stock prices of {', '.join(final_stocks)}, and how is the performance over the past 6 months in terms of percentage change? 
        Start by retrieving the full name of each stock and use it for all future requests.
        Prepare a figure of the normalized price of these stocks and save it to a file named normalized_prices.png. Include information about, if applicable: 
        * CAGR for the last 5 years
        * Forward P/E
        * Price to book
        * Debt/Eq
        * ROE
        * Analyze the correlation between the stocks
        Do not use a solution that requires an API key.
        If some of the data does not makes sense, such as a price of 0, change the query and re-try.
        Do not hallucinate, if any data is unavailable, fill it with "N/A"
        """,

        """Investigate possible reasons of the stock performance leveraging market news headlines from Bing News or Google Search. Retrieve news headlines using python and return them. Use the full name stocks to retrieve headlines. Retrieve at least 10 headlines per stock. Do not use a solution that requires an API key. Do not perform a sentiment analysis."""
    ]

    with st.spinner("Agents working on the analysis...."):
        chat_results = autogen.initiate_chats(
            [
                {
                    "sender": user_proxy_auto,
                    "recipient": financial_assistant,
                    "message": financial_tasks[0],
                    "silent": False,
                    "summary_method": "reflection_with_llm",
                    "summary_args": {
                        "summary_prompt": 
                            "Return the stock prices of the stocks, their performance and all other metrics "
                            "into a JSON object only. Provide the name of all figure files created. Provide the full name of each stock."
                    },
                    "clear_history": False,
                    "carryover": "Wait for confirmation of code execution before terminating the conversation. Verify that the data is not completely composed of NaN values. Reply TERMINATE in the end when everything is done."
                },
                {
                    "sender": user_proxy_auto,
                    "recipient": research_assistant,
                    "message": financial_tasks[1],
                    "silent": False,
                    "summary_method": "reflection_with_llm",
                    "summary_args": {
                        "summary_prompt": 
                            "Provide the news headlines as a paragraph for each stock, be precise but do not consider news events that are vague, return the result as a JSON object only."
                    },
                    "clear_history": False,
                    "carryover": "Wait for confirmation of code execution before terminating the conversation. Reply TERMINATE in the end when everything is done."
                },
                {
                    "sender": critic,
                    "recipient": writer,
                    "message": writing_tasks[0],
                    "carryover": "I want to include a figure and a table of the provided data in the financial report.",
                    "max_turns": 2,
                    "summary_method": "last_msg",
                }
            ]
        )

    image_path = "./coding/normalized_prices.png"


    if os.path.exists(image_path):
        st.image(image_path)
    else:
        st.write("Sorry, the image could not be displayed.")
    st.markdown(chat_results[-1].chat_history[-1]["content"])