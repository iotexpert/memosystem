from os.path import exists,join
from shutil import copy

from memos.create import create_app
from memos.models.Memo import Memo

temp_sl = join("memos","static","config","settings_local.py")

if not exists("settings_local.py") and exists(temp_sl):
    copy(temp_sl,"settings_local.py")    

try:
    import settings_local
except ImportError:
    pass

app = create_app()

if __name__ == '__main__':
    app.run(debug=False)
