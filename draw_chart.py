import numpy as np
import streamlit as st
import pandas as pd
import re
from openai import OpenAI
import matplotlib.pyplot as plt

# Define the model to use
MODEL_NAME = "gpt-3.5-turbo"


def handle_openai_draw_chart(chart_desc_text, data):
    """
    Handle the OpenAI query and display the response.

    Parameters:
    - df: DataFrame containing the data
    - column_names: List of column names in the DataFrame
    """

    # Create a text area for user input
    # query = st.text_area(
    #     "Enter your Prompt:",
    #     placeholder="Prompt tips: Use plotting related keywords such as 'Plots' or 'Charts' or 'Subplots'. Prompts must be concise and clear, example 'Bar plot for the first ten rows.'",
    #     help="""
    #         How an ideal prompt should look like? *Feel free to copy the format and adapt to your own dataset.*
    #
    #         ```
    #         - Subplot 1: Line plot of the whole spectra.
    #         - Subplot 2: Zoom into the spectra in region 1000 and 1200.
    #         - Subplot 3: Compare the area of whole spectra and zoom spectra as Bar Plot.
    #         - Subplot 4: Area curve of the zoom spectra.
    #         ```
    #         """,
    # )


    # Ensure the query is not empty
    # if query and query.strip() != "":
    if chart_desc_text != "":
        # Define the prompt content
        prompt_content = f"""
        
        The user want to draw {chart_desc_text} 
        
        The dataset is this: {data}
        
        You need analyze the data, covert it to a good DataFrame for the charts that user want, 
        
        Before plotting, ensure the data is ready:
        1. Check if columns that are supposed to be numeric are recognized as such. If not, attempt to convert them.
        2. Handle NaN values by filling with mean or median.
        
        Use package Pandas and Matplotlib ONLY.
        Provide SINGLE CODE BLOCK with a solution using Pandas and Matplotlib plots in a single figure to address the following query:
        
         {chart_desc_text} 

        - USE SINGLE CODE BLOCK with a solution. 
        - Do NOT EXPLAIN the code 
        - DO NOT COMMENT the code. 
        - ALWAYS WRAP UP THE CODE IN A SINGLE CODE BLOCK.
        - The code block must start and end with ```
        
        - Example code format ```code```
    
        - Colors to use for background and axes of the figure : #F0F0F6
        - Try to use the following color palette for coloring the plots : #8f63ee #ced5ce #a27bf6 #3d3b41
        
        """

        # Define the messages for the OpenAI model
        messages = [
            {
                "role": "system",
                "content": "You are a helpful Data Visualization assistant who gives a single block without explaining or commenting the code to plot. IF ANYTHING NOT ABOUT THE DATA, JUST politely respond that you don't know.",
            },
            {"role": "user", "content": prompt_content},
        ]

        # Call OpenAI and display the response
        with st.status("📟 *Prompting is the new programming*..."):
            with st.chat_message("assistant", avatar="📊"):
                botmsg = st.empty()
                response = []
                client = OpenAI(
                    # This is the default and can be omitted
                    api_key=st.secrets.openai_api_key,
                )

                for chunk in client.chat.completions.create(
                        model=MODEL_NAME, messages=messages, stream=True
                ):
                    text = chunk.choices[0].delta.content
                    if text:
                        response.append(text)
                        result = "".join(response).strip()
                        botmsg.write(result)
        execute_openai_code(result)


def extract_code_from_markdown(md_text):
    """
    Extract Python code from markdown text.

    Parameters:
    - md_text: Markdown text containing the code

    Returns:
    - The extracted Python code
    """
    # Extract code between the delimiters
    code_blocks = re.findall(r"```(python)?(.*?)```", md_text, re.DOTALL)

    # Strip leading and trailing whitespace and join the code blocks
    code = "\n".join([block[1].strip() for block in code_blocks])

    return code


def execute_openai_code(response_text: str):
    """
    Execute the code provided by OpenAI in the app.

    Parameters:
    - response_text: The response text from OpenAI
    - df: DataFrame containing the data
    - query: The user's query
    """

    # Extract code from the response text
    code = extract_code_from_markdown(response_text)

    # If there's code in the response, try to execute it
    if code:
        try:
            exec(code)
            st.pyplot()
        except Exception as e:
            error_message = str(e)
            st.error(
                f"📟 Apologies, failed to execute the code due to the error: {error_message}"
            )
            st.warning(
                """
                📟 Check the error message and the code executed above to investigate further.

                Pro tips:
                - Tweak your prompts to overcome the error 
                - Use the words 'Plot'/ 'Subplot'
                - Use simpler, concise words
                - Remember, I'm specialized in displaying charts not in conveying information about the dataset
            """
            )
    else:
        st.write(response_text)


def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncols=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')

    return fig, ax
