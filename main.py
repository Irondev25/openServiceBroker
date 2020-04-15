import os

from broker import create_app


def main():
    """
    Main class for local execution.

    Use a proper webserver in production!
    """
    port = int(os.getenv('PORT', '5050'))
    app = create_app()
    app.run('127.0.0.1', port=port, debug=True)


if __name__ == '__main__':
    main()
