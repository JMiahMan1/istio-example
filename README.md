# Setting Up Test Applications with Istio on Minikube in Fedora Linux

This guide provides step-by-step instructions for setting up multiple test applications that communicate over an Istio service mesh installed on Minikube running on Fedora Linux. The test setup includes two very simple microservices written in two languages:

-   **Service A (Python/Flask)**: Exposes an API and calls Service B.
    
-   **Service B (Ruby/Sinatra)**: Responds to API requests from Service A.
    

## 1. Install and Set Up Minikube on Fedora

## Installing Prerequisites on Fedora 
Let’s step through the installation of the necessary prerequisites on Fedora. These steps ensure that your system is properly configured before installing Minikube.

### Updating Fedora

Before taking such an edeavor you should always update your Fedora system to ensure you have the latest packages:

```bash
sudo dnf update
```
This command updates all installed packages to their latest versions.

### Installing Docker

Docker is a popular containerization platform. Alternatively, you can use Podman, a daemonless container engine. In this example where just cover how to install Docker:

```bash
sudo dnf install docker-ce --nobest -y
sudo systemctl enable --now docker
```

To allow your user account to manage docker, add it to the  `docker`  group:

```bash
sudo usermod -a -G docker $(whoami)
newgrp docker
```
This step is necessary for non-root users to interact with docker. The  `newgrp docker`  command updates your current session to recognize the group membership.


### Installing  `kubectl`

`kubectl`  is the Kubernetes command-line tool that allows you to interact with your Kubernetes cluster. Install it using:

```bash
sudo dnf install kubectl -y
```

This command installs  `kubectl`  from the Fedora repositories.

## Installing Minikube on Fedora

With the prerequisites installed, let’s proceed with installing Minikube on Fedora. Here are the detailed steps:

### Downloading the Minikube Binary

Download the latest Minikube binary using  curl:

```bash
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/
```

The above commands download the Minikube binary, make it executable, and move it to  `/usr/local/bin/`, ensuring it’s in your system’s PATH.

### Verifying the Installation

Verify that Minikube is installed correctly by checking its version:

```bash
minikube version
```

This command displays the installed Minikube version. A successful output confirms that Minikube is correctly installed.

### Start Minikube

Launch a Minikube cluster with sufficient resources:

```
minikube start --driver=docker --cpus=4 --memory=16g
```

----------

## 2. Install Istio on Minikube

### a. Download and Install Istio

```
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
```

### b. Install Istio

```
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
```

----------

## 3. Create Test Applications

### a. Service A (Python/Flask)

#### `service_a.py`

```
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/call-service-b', methods=['GET'])
def call_service_b():
    try:
        response = requests.get("http://service-b:5000/message")
        return jsonify({"message": "Response from service-b", "data": response.json()})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "service-a is running"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

#### `Dockerfile`

```
FROM python:3.9-slim
WORKDIR /app
COPY service_a.py /app
RUN pip install flask requests
EXPOSE 8080
CMD ["python", "service_a.py"]
```

### b. Service B (Ruby/Sinatra)

#### `service_b.rb`

```
require 'sinatra'
require 'json'

set :bind, '0.0.0.0'  
set :port, 5000  
# This is needed to prevent the error:  
# WARN -- : attack prevented by Rack::Protection::HostAuthorization  
set :environment, :production

get '/message' do
  content_type :json
  { message: "Hello from service-b" }.to_json
end

get '/health' do
  content_type :json
  { status: "service-b is running" }.to_json
end
```

#### `Dockerfile`

```
FROM ruby:3.0
WORKDIR /app
COPY service_b.rb /app
RUN gem install rackup puma sinatra
EXPOSE 5000
CMD ["ruby", "service_b.rb"]
```

----------

## 4. Deploy Applications to Minikube

### a. Build and Deploy Services

```
eval $(minikube docker-env)
docker build -t service-a:latest -f Dockerfile-service-a .
docker build -t service-b:latest -f Dockerfile-service-b .
kubectl apply -f service-a-deployment.yaml
kubectl apply -f service-b-deployment.yaml
```

### b. Kubernetes Deployment Manifests

#### `service-a-deployment.yaml`

```
apiVersion: v1
kind: Service
metadata:
  name: service-a
  labels:
    app: service-a
    service: service-a
spec:
  ports:
  - port: 8080
    name: http
  selector:
    app: service-a
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: services-service-a
  labels:
    account: service-a
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-a-v1
  labels:
    app: service-a
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: service-a
      version: v1
  template:
    metadata:
      labels:
        app: service-a
        version: v1
    spec:
      serviceAccountName: services-service-a
      containers:
      - name: details
        image: service-a:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
```

#### `service-b-deployment.yaml`

```
apiVersion: v1
kind: Service
metadata:
  name: service-b
  labels:
    app: service-b
    service: service-b
spec:
  ports:
  - port: 5000
    name: http
  selector:
    app: service-b
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: services-service-b
  labels:
    account: service-b
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: service-b-v1
  labels:
    app: service-b
    version: v1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: service-b
      version: v1
  template:
    metadata:
      labels:
        app: service-b
        version: v1
    spec:
      serviceAccountName: services-service-b
      containers:
      - name: service-b
        image: service-b:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
```

----------

## 5. Configure Istio Routing

#### `gateway.yaml`

```
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
    name: service-a-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: service-a
spec:
  hosts:
  - "*"
  gateways:
  - service-a-gateway
  http:
  - match:
    - uri:
        exact: /health
    - uri:
        exact: /call-service-b
    route:
    - destination:
        host: service-a
        port:
          number: 8080
                        
```
#### Apply Configuration

```
kubectl apply -f gateway.yaml
```

----------

## 6. Test the Setup

### a. Verify Services

```
kubectl get pods
```

### b. Access Services

```
export INGRESS_HOST=$(minikube ip)
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
```

#### Test `service-a`

```
curl http://$INGRESS_HOST:$INGRESS_PORT/health
```

#### Test Inter-Service Communication (`service-a` calling `service-b`)

```
curl http://$INGRESS_HOST:$INGRESS_PORT/call-service-b
```

----------

## 7. Cleanup

```
kubectl delete -f service-a-deployment.yaml
kubectl delete -f service-b-deployment.yaml
kubectl delete -f gateway.yaml
istioctl uninstall --purge
minikube stop
```

----------

## Summary

-   **Service A (Python/Flask)** calls **Service B (Ruby/Sinatra)** using HTTP.
    
-   Istio manages service-to-service communication within Minikube.
    
-   API endpoints allow direct and inter-service testing.
    
This setup provides a fully functional Istio-enabled microservices architecture in Minikube on Fedora Linux.
