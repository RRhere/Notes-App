import os
from dotenv import load_dotenv
from website import create_app

load_dotenv()

app = create_app()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(
        debug=debug_mode,
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        use_reloader=debug_mode
    )    