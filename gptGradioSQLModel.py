import gradio as gr
from openai import OpenAI
import pandas as pd
from sqlmodel import SQLModel, create_engine
import sqlalchemy
import plotly.express as px

# GPT API Configuration
client = OpenAI(
    api_key=""
)

# MySQL Database Connection
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_DATABASE = "db_name"


DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
)
engine = create_engine(DATABASE_URL)


# Function to initialize the database schema
def initialize_database():
    SQLModel.metadata.create_all(engine)


# Function to fetch the schema of all tables in the database
def get_database_schema(engine):
    schema = {}
    with engine.connect() as conn:
        inspector = sqlalchemy.inspect(conn)
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema[table_name] = [f"{col['name']} ({col['type']})" for col in columns]
    return schema


# Function to generate SQL from a natural language query
def generate_sql(nl_query, database_schema):
    schema_description = "\n".join(
        f"Table: {table}\nColumns: {', '.join(columns)}"
        for table, columns in database_schema.items()
    )
    prompt = (
        f"The following is the schema of the database:\n{schema_description}\n\n"
        f"Write an SQL query to answer the question:\n'{nl_query}'"
        f"Return an executable query, that is only the query without \\n, or any explanations or quotes."
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful SQL assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


# Function to clean SQL queries
def clean_sql_query(generated_sql):
    generated_sql = generated_sql.strip().replace("`", "").replace("\n", " ")
    if generated_sql.startswith("sql"):
        return generated_sql[3:].strip()
    return generated_sql.strip()


# Function to generate Plotly visualization code
def generate_plotly_visualization_code(df):
    sample_data = df.head(5).to_string(index=False)
    prompt = (
        f"The following is a sample of a DataFrame:\n{sample_data}\n\n"
        f"Write Python code using Plotly to visualize this data. Use a bar chart if the data contains categories and numerical values."
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
def query_and_visualize(nl_query):
    try:
        database_schema = get_database_schema(engine)
        
        # Generate SQL query
        raw_sql_query = generate_sql(nl_query, database_schema)
        sql_query = clean_sql_query(raw_sql_query)
        
        # Fetch query results
        result_df = pd.read_sql(sql_query, engine)
        raw_vis_code = generate_plotly_visualization_code(result_df)
        
        vis_code = clean_visualization_code(raw_vis_code)
        fig = execute_plotly_visualization_code(vis_code, result_df)
        return fig, result_df, vis_code
    except Exception as e:
        return f"{result_df}", None


with gr.Blocks() as demo:
    gr.Markdown("# Natural Language Data Insights with MySQL")
    gr.Markdown(f"Enter a natural language query to retrieve and visualize data from your {MYSQL_DATABASE} database.")
    
    # Centered input
    with gr.Row():
        nl_query_input = gr.Textbox(label="Enter your natural language query:", interactive=True)
    with gr.Row():
        query_button = gr.Button("Submit Query")
    with gr.Row():
        table_output = gr.Dataframe(label="Query Results")

    # Outputs below input
    with gr.Row():
        visualize_output = gr.Plot(label="Visualization")

    # Button action
    query_button.click(query_and_visualize, inputs=nl_query_input, outputs=[visualize_output, table_output])

# Launch the interface
demo.launch()

# iface.launch()
