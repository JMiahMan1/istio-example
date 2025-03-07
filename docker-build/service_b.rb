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

require 'sinatra'
require 'json'

set :bind, '0.0.0.0'
set :port, 5000
# This is needed to prevent the error:
# WARN -- : attack prevented by Rack::Protection::HostAuthorization
set :environment, :production

# Endpoint to return a simple message
get '/message' do
  content_type :json
  { message: "Hello from service-b" }.to_json
end

# Health check endpoint
get '/health' do
  content_type :json
  { status: "service-b is running" }.to_json
end
