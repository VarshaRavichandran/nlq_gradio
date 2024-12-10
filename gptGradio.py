import pandas as pd
import gradio as gr
from openai import OpenAI
import plotly.express as px
from io import StringIO


# OpenAI API Configuration
client = OpenAI(
    api_key=""
)

# Function to generate insights
def generate_insights(prompt, df):
    dataset_sample = df.head(10).to_string(index=False)
    complete_prompt = (
        f"The following is a dataset:\n\n{dataset_sample}\n\n"
        f"{prompt}\n\n"
        "Please provide the answer without explaining calculations or steps in a Dataframe format along with column headers as keys"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful data analysis assistant."},
            {"role": "user", "content": complete_prompt}
        ],
        max_tokens=100,
        temperature=0.8
    )
    print(response.choices[0].message.content.strip())
    print("\n\nHERE\n\n")
    return response.choices[0].message.content.strip()

def clean_response(response):
    print(response)
    print("HeRERE\n\n")
    response = response.replace('`', '')
    response = response.replace('plaintext', '')
    print(response)

    # Convert string to DataFrame
    data = StringIO(response.strip())  # Remove extra leading/trailing spaces
    df = pd.read_csv(data, delim_whitespace=True)  # Use whitespace as delimiter

    print(df)
    return df

# Gradio App
def analyze_dataset(file, prompt):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        # Generate insights
        response = generate_insights(prompt, df)
        cleaned_response = clean_response(response)
        return cleaned_response, df.head()
    except Exception as e:
        return None, f"{response}"
        

# Function to generate Plotly visualization code
def generate_plotly_visualization_code(df):
    sample_data = df.head(5).to_string(index=False)
    prompt = (
        f"The following is a sample of a DataFrame:\n{sample_data}\n\n"
        f"Write Python code using Plotly to visualize this data. Use a bar chart only if the data contains categories and numerical values."
        f"Ensure the chart is interactive and aesthetically pleasing with black template."
        f"Assume the DataFrame is already defined as 'df' and return only the Python code for the visualization."
        f"Since this is just a sample, give me only a generic code without any explanations"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful data visualization assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

def clean_visualization_code(code):
    """
    Cleans GPT-generated visualization code by removing redefinitions of the DataFrame.
    """
    lines = code.splitlines()
    cleaned_lines = []
    inside_df_definition = False
    
    for line in lines:
        # Skip DataFrame definitions

        line = line.replace('```', '')
        line = line.replace('python', '')
        if "pd.DataFrame(" in line:
            inside_df_definition = True
        if inside_df_definition and line.strip() == ")":
            inside_df_definition = False
            continue
        if not inside_df_definition:
            # Replace fig.show() with 
            if "fig.show()" in line:
                line = ""
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# Function to execute Plotly visualization code
def execute_plotly_visualization_code(code, df):
    local_vars = {"df": df, "px": px}
    exec(code, {}, local_vars)
    return local_vars["fig"]

# Gradio App
def analyze_and_visualize(file, nl_query):
    try:

        # Fetch query results
        result_df, preview = analyze_dataset(file, nl_query)
        raw_vis_code = generate_plotly_visualization_code(result_df)
        
        vis_code = clean_visualization_code(raw_vis_code)
        print(vis_code)
        fig = execute_plotly_visualization_code(vis_code, result_df)
        return preview, result_df.head(), fig
    except Exception as e:
        return f"{preview}", None

with gr.Blocks() as demo:
    gr.Markdown("# AI-Powered Dashboard")
    gr.Markdown("Enter a natural language query to retrieve and visualize data from the uploaded dataset.")
    
    # Centered input
    with gr.Row():
        file_input = gr.File(label="Upload your CSV file")
        question_input = gr.Textbox(label="Ask a question about your dataset")
    # with gr.Row():
    analyze_button = gr.Button("Analyze Dataset")
        
    # Outputs: Dataset Preview and AI-Generated Insights
    with gr.Row():
        dataset_preview = gr.Dataframe(label="Dataset Preview")
        ai_insights = gr.Textbox(label="AI-Generated Insights")
    # Outputs below input
    with gr.Row():
        visualize_output = gr.Plot(label="Visualization")

    # Button action

    analyze_button.click(analyze_and_visualize, inputs=[file_input, question_input], outputs=[dataset_preview, ai_insights, visualize_output])

# Launch the interface
demo.launch()