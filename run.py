"""啟動網站。

開發／預覽：  python run.py            （http://127.0.0.1:8000）
正式環境：    python run.py --prod     （使用 Waitress，適合 Windows 或 Linux 伺服器）
"""
import os
import sys

from kt import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("KT_HOST", "127.0.0.1")
    port = int(os.environ.get("KT_PORT", "8000"))
    if "--prod" in sys.argv:
        from waitress import serve
        print(f"網站已啟動：http://{host}:{port}")
        serve(app, host=host, port=port, threads=8)
    else:
        app.run(host=host, port=port, debug=os.environ.get("KT_DEBUG") == "1")
