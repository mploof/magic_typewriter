import yaml

with open("./config.yaml", 'r') as file:
    config = yaml.safe_load(file)

context_dir = config["context_dir"]
default_context_file = config["default_context_file"]
    
with open(f"./{context_dir}/{default_context_file}", "r") as f:
    default_context = f.read().strip()
       
with open(f"./keys/{config['gpt_key_file_name']}", "r") as f:
    OPENAI_API_KEY = f.read().strip()
    
with open(f"./keys/{config['xi_key_file_name']}", "r") as f:
    XI_LABS_API_KEY = f.read().strip()
