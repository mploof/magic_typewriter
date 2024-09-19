import yaml

def get_config():
    with open("config.yaml", "r") as file:
       config = yaml.safe_load(file)
    return config

config = get_config()

context_dir = config["context_dir"]
default_context_file = config["default_context_file"]
ai = config["ai"]
    
with open(f"./{context_dir}/{default_context_file}", "r") as f:
    default_context = f.read().strip()
       
with open(f"./keys/{config['gpt_key_file_name']}", "r") as f:
    OPENAI_API_KEY = f.read().strip()
    
with open(f"./keys/{config['xi_key_file_name']}", "r") as f:
    XI_LABS_API_KEY = f.read().strip()
    
with open(f"./keys/{config['claude_key_file_name']}", "r") as f:
    ANTHROPIC_API_KEY = f.read().strip()

