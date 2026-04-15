from dotenv import load_dotenv
import os

_ = load_dotenv()

NUM_CPUS = os.cpu_count()
