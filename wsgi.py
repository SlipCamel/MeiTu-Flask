import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
flaskenv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.flaskenv')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)  # override=True: 覆写已存在的变量
    load_dotenv(flaskenv_path)
from MeiTu import create_app

app = create_app()

# if __name__ == '__main__':
#     app.run()