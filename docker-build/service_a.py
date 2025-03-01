#########################################################################################
#    The MIT License (MIT)
#    Copyright (c) 2025 Jeremiah Summers
#
#         Permission is hereby granted, free of charge, to any person obtaining a copy
#         of this software and associated documentation files (the "Software"), to deal
#         in the Software without restriction, including without limitation the rights
#         to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#         copies of the Software, and to permit persons to whom the Software is
#         furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#    
#         THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#         IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#         FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#         AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#         LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#         OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#         THE SOFTWARE.
#########################################################################################

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define an endpoint to call service-b
@app.route('/call-service-b', methods=['GET'])
def call_service_b():
    try:
        response = requests.get("http://service-b:5000/message")  # Calls service-b
        return jsonify({"message": "Response from service-b", "data": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "service-a is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
