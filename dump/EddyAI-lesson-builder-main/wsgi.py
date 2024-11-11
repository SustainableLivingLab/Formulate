from app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(app.config['APP_PORT']),
        debug=bool(app.config['APP_DEBUG']),
    )