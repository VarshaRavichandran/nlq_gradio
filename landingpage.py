import gradio as gr
import time
import subprocess
import webbrowser


port_add = 0


# Function to launch the first script
def launch_script_1():
    global port_add 
    port_add += 1
    subprocess.Popen(["python3", "gptGradioSQLModel.py"])
    time.sleep(2)
    webbrowser.open(f"http://127.0.0.1:{7860+port_add}") 
    return "Launching SQLModel-based Gradio app. Check the terminal or browser."

# Function to launch the second script
def launch_script_2():
    # Use subprocess to run the second script (gptGradio.py)
    global port_add 
    port_add += 1
    subprocess.Popen(["python3", "gptGradio.py"])
    time.sleep(2)
    webbrowser.open(f"http://127.0.0.1:{7860+port_add}") 
    return "Launching GPT-powered CSV analysis app. Check the terminal or browser."

# Landing Page
with gr.Blocks() as landing_page:
    gr.Markdown("# Welcome to the AI-Powered App Suite")

    with gr.Row(elem_id="centered-container"):
        with gr.Column(scale=1, min_width=500):
            with gr.Row():
                # Option for the first app
                btn_script_1 = gr.Button("Explore internal database")
                # Option for the second app
                btn_script_2 = gr.Button("Explore external dataset ")

            with gr.Row():
                output = gr.Textbox(label="Launch status", interactive=False)

            # Button actions
            btn_script_1.click(launch_script_1, inputs=[], outputs=output)
            btn_script_2.click(launch_script_2, inputs=[], outputs=output)

# Launch the landing page
# Add custom CSS for centering
landing_page.css = """
#component-4 {
    display: flex;
    justify-content: center;
    gap: 1em;
    margin-bottom: 2em;
    margin-top: 12em;
}
"""

'''
landing_page.css = """
#centered-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
}
#title {
    font-size: 2em;
    font-weight: bold;
    margin-bottom: 1em;
}
#subtitle {
    font-size: 1.5em;
    margin-bottom: 2em;
}
#component-4 {
    display: flex;
    justify-content: center;
    gap: 1em;
    margin-bottom: 2em;
}

#component-5, #component-6 {
    font-size: 1.2em;
    padding: 1em 2em;
    border-radius: 10px;
    border: 1px solid #ccc;
    background-color: #666;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
}

#component-5:hover, #component-6:hover {
    background-color: #444;
    transform: scale(1.05);
}

#component-7 {
    margin-top: 2em;
}

"""
'''

landing_page.launch()
