from os.path import exists,join
from shutil import copy

temp_sl = join("memos","static","config","settings_local.py")

if not exists("settings_local.py") and exists(temp_sl):
    copy(temp_sl,"settings_local.py")    

try:
    import settings_local
except ImportError:
    pass


from memos import create_app
from memos.models.Memo import Memo

app = create_app()
@app.context_processor
def inject_pinned():
    return dict(get_pinned=Memo.get_pinned)
    
if __name__ == '__main__':
    app.run(debug=True)
