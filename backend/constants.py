import os

# import dj_database_url
from dotenv import load_dotenv

#  load env
load_dotenv()


POINT_PER_STEP = float(os.getenv("POINT_PER_STEP"))
MAX_STEP_TO_REWARD = int(os.getenv("MAX_STEP_TO_REWARD"))
MIN_STEP_TO_REWARD = int(os.getenv("MIN_STEP_TO_REWARD"))
REWARD_FOR_INVITING = int(os.getenv("REWARD_FOR_INVITING"))
REWARD_FOR_INVITED = int(os.getenv("REWARD_FOR_INVITED"))
