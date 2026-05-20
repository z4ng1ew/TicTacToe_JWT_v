from di import Container

if __name__ == "__main__":
    container = Container()
    app       = container.get_app()

    print("Сервер запущен: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)