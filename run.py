from app import app

if __name__ == '__main__':
    # print ("Running API...")
    app.run(host='0.0.0.0', port=10206, debug=True)