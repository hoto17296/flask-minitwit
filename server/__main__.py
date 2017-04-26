import os
from server import app

app.run(port=int(os.environ.get('PORT')))
