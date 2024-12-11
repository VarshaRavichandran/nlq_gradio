# nlq_gradio
GPT powered Exploratory Data Analysis with Gradio and SQLModel

## Prerequisites
OpenAI API is a paid service. Choose a plan that is sufficient for your data needs and take note of the openAI API Key, say <api_key>
The product requires Python 3.

## Initial setup
1. Clone the repository
2. Install required dependencies
```
    pip install sqlmodel sqlalchemy pandas openai gradio plotly
```
3. Navigate to the repository and edit the following with your details:

   a. In both gptGradio.py and gptGradioSQLModel.py

   Replace
       
        client = OpenAI(
            api_key=""
        )
    with the key generated initially. example: <api_key>
    
        client = OpenAI(
            api_key="<api_key>"
        )
   
    b. In gptGradioSQLModel.py
   
    Replace the following with the database you want to connect to and the corresponding details.
   
        # MySQL Database Connection
        MYSQL_HOST = "host"
        MYSQL_USER = "root"
        MYSQL_PASSWORD = "password"
        MYSQL_DATABASE = "db_name"

4. Run the 'landingpage.py' file

       path/to/your/python /path/to/landingpage.py
