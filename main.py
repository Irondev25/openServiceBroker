import os

from broker import create_app
from dotenv import load_dotenv


def main():
    """
    Main class for local execution.

    Use a proper webserver in production!
    """
    load_dotenv('.env')
    port = int(os.getenv('PORT', '5050'))
    app = create_app()
    app.run('127.0.0.1', port=port, debug=True)


if __name__ == '__main__':
    main()
