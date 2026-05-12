from dotenv import load_dotenv

load_dotenv()

import uvicorn

from a2a_agent.a2a_server import create_app
from a2a_agent.config import settings
from a2a_agent.tracing import init_tracing


def main():
    init_tracing()
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=settings.agent_port, log_level="info")


if __name__ == "__main__":
    main()
