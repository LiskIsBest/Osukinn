from dotenv import load_dotenv
import os
load_dotenv()

from Site import create_app

app = create_app(
    key=os.getenv('SECRET_KEY'),
    config=os.getenv('FLASK_ENV'),
    flApp=os.getenv('FLASK_APP'))

# if __name__ == "__main__":
#     app.run()