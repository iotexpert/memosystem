from docmgr import create_app

try:
    import settings_local
except ImportError:
    pass

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
