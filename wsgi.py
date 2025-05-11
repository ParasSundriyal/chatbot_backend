from app import app

if __name__ == "__main__":
    from waitress import serve
    print("Starting server on http://localhost:5000")
    serve(app, host="0.0.0.0", port=5000)
