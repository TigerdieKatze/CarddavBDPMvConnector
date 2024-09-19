import json
import logging

CONFIG_FILE = '/app/config/config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

CONFIG = load_config()

# Configure logging
logging.basicConfig(level=getattr(logging, CONFIG.get("LOG_LEVEL", "INFO")),
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)