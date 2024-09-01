## How to run this project ??
### 1. First clone the project 
```bash
git clone https://github.com/yatndeep-vunet/vunet_lms_monitoring.git
```
### 2. Check the docker is installed or not ??

```bash
docker --version
```
#### If not please follow the link <a hrer="https://docs.docker.com/engine/install/ubuntu/">Docker Installation</a> for ubuntu .

### 3. Run the docker build command .

```bash
docker compose up --build
```

### 4. Now you can see :
#### 4.1 The LMS Application  
```
http://<host>:8000
```

#### 4.2 Prometheus Dashboard
```
http://<host>:9091
```

#### 4.3 Grafana Dashboard 
```
http://<host>:3000
```
### 5 Add the datasource as Prometheus with the url 
```
http://prometheus:9090
```
### 6. Now create a dashboard with the datasource prometheus