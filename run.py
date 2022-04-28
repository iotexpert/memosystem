try:
    import settings_local
except ImportError:
    pass
from docmgr import create_app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
