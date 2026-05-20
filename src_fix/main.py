import webbrowser
import threading
import time
from datasource.db import init_db
from di.app_box import DependencyBox


def launch_browser() -> None:
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000/")


if __name__ == "__main__":
    init_db()
    box: DependencyBox = DependencyBox()
    web_app = box.get("web_app")
    threading.Thread(target=launch_browser, daemon=True).start()
    print("Сервер запущен: http://127.0.0.1:5000")
    web_app.run(host="0.0.0.0", port=5000, debug=True)
