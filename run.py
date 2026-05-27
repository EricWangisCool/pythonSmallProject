from src import create_app

app = create_app()

if __name__ == "__main__":
    print("Starting Flask application on http://localhost:19191")
    app.run(host="0.0.0.0", port=19191, debug=True)
