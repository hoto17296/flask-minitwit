import os
from server import app

app.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 80)),
    debug=None
)
