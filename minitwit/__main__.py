import os
from minitwit import app

app.run(port=int(os.environ.get('PORT')))
