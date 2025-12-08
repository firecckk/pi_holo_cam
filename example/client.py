from openai import OpenAI

import sys
import os
parent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(parent_dir)
import config
API_KEY = config.API_KEY
client = OpenAI(api_key=config.API_KEY)