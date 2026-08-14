import uvicorn
from opentrust.api import app
from opentrust.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level)
