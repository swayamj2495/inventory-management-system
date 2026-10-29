# Inventory Management System


This project is an end-to-end, full-stack inventory management system featuring:

- A **Modern Web Frontend** built with clean Jinja2 templates, custom CSS, Lucide icons, and responsive UI.
- A **Flask API** built with object-oriented design and SQLAlchemy ORM.
- **MySQL** integration with a normalized relational schema (`Products`, `Orders`, `Order_Items`).
- **Concurrency control** with thread locks (`threading.Lock`) and database transactions (`with_for_update()`) for handling simultaneous orders safely.
- **Containerization** using Docker and Docker Compose.
- **Kubernetes orchestration** configurations for scalable cloud or local deployment.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features & User Interface](#features--user-interface)
  - [Frontend Views](#frontend-views)
  - [Design System & Low-Stock Rules](#design-system--low-stock-rules)
- [Project Architecture](#project-architecture)
- [API Endpoints](#api-endpoints)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
  - [3. Install Python Dependencies](#3-install-python-dependencies)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Database Setup](#5-database-setup)
  - [6. Run the Flask Application Locally](#6-run-the-flask-application-locally)
- [Containerization with Docker Compose](#containerization-with-docker-compose)
  - [1. Build and Run Containers](#1-build-and-run-containers)
  - [2. Verify Application and Endpoints](#2-verify-application-and-endpoints)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [1. Prerequisites for Kubernetes](#1-prerequisites-for-kubernetes)
  - [2. Using Local Images in Kubernetes](#2-using-local-images-in-kubernetes)
  - [3. Kubernetes YAML Configurations](#3-kubernetes-yaml-configurations)
  - [4. Deploying to Kubernetes](#4-deploying-to-kubernetes)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

This application provides a comprehensive inventory and order management system with:

- **Interactive Dashboard:** Live inventory metrics, low-stock alerts, and recent activities.
- **Product Management:** Add new items with prices and stock levels, view existing inventory.
- **Dynamic Order Processing:** Multi-item orders with atomic stock validation and deduction.
- **Reports:** Overview tables for products and orders with status tracking and manual refresh.
- **Docker & Compose:** Multi-container setup orchestrating the Flask app and MySQL service.
- **Kubernetes Ready:** Manifests for scalable cluster deployment.

---

## Features & User Interface

### Frontend Views

| Page | Route | Description |
|---|---|---|
| **Dashboard** | `GET /` | Real-time overview cards (Total Products, Total Orders, Total Stock, Low Stock Items) and recent product/order tables. |
| **Products** | `GET /products` | Product creation form with validation, price tracking, and existing product inventory table. |
| **Place Order** | `GET /place-order` | Multi-item order placement interface with live stock display, row-level removals, duplicate item deduplication, and immediate confirmation. |
| **Reports** | `GET /reports` | Dedicated side-by-side reporting for products and customer orders with formatted dates and status badges. |

### Design System & Low-Stock Rules

- **Theme:** Dark navy sidebar navigation, clean light-grey canvas, responsive white cards, and Lucide icons.
- **Action Colors:** Blue primary buttons, green for completed orders/order submission, amber warnings, and red for alerts/removals.
- **Low-Stock Threshold:** Configured globally as `LOW_STOCK_THRESHOLD = 5`.
  - Stock `≤ 5`: Highlighted in red badge/text and counted in the dashboard "Low Stock Items" card.
  - Stock `6 - 10`: Displayed with amber warning indicator.

---

## Project Architecture

```
inventory-management-system/
├── app.py                  # Flask application & API routes
├── Dockerfile              # App container image definition
├── docker-compose.yaml     # Compose configuration for MySQL & Flask
├── requirements.txt        # Python package dependencies
├── .env                    # Environment configuration (ignored in git)
├── .gitignore              # Git ignore rules
├── database/
│   └── schema.sql          # MySQL database schema definition
├── static/
│   ├── css/
│   │   └── style.css       # Custom design system & responsive layout
│   └── js/
│       └── app.js          # Shared frontend API helpers & UI utilities
└── templates/
    ├── base.html           # Layout shell with dark navy sidebar & navigation
    ├── dashboard.html      # Metrics overview & recent activity tables
    ├── products.html       # Add product form & catalog table
    ├── place_order.html    # Order builder & submission form
    ├── reports.html        # Comprehensive products & orders reports
    └── index.html          # Legacy route redirect
```

---

## API Endpoints

### UI Routes
- `GET /` — Renders Dashboard view.
- `GET /products` — Renders Product Management view.
- `GET /place-order` — Renders Order Placement view.
- `GET /reports` — Renders System Reports view.

### JSON API Endpoints
- `POST /add_product` — Add a new product.
  - Payload: `{"name": "Mouse", "description": "Wireless mouse", "price": 25.50, "stock_quantity": 40}`
- `POST /place_order` — Place a new customer order with inventory deduction.
  - Payload: `{"customer_id": 101, "items": [{"product_id": 1, "quantity": 2}]}`
- `GET /api/report` — Extended JSON data for UI dashboards (includes prices, descriptions, and ISO dates).
- `GET /report` — Original legacy report endpoint returning basic product and order summaries.

---

## Prerequisites

- **Operating System:** Linux, macOS, or Windows.
- **Docker & Docker Compose:** Installed and running.
- **Python 3.8+** & **MySQL client** (if running outside Docker).
- **Kubernetes:** Docker Desktop Kubernetes, Minikube, or a cloud cluster (optional).

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/inventory-management-system.git
cd inventory-management-system
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```ini
DB_USER=inventory_user
DB_PASSWORD=inventory_pass
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=inventory_db
SECRET_KEY=your_secret_key
```

### 5. Database Setup

Ensure MySQL is running on your configured host/port, then load the schema:

```bash
mysql -u inventory_user -p -h 127.0.0.1 -P 3307 inventory_db < database/schema.sql
```

*(Alternatively, you can start the MySQL container via Docker Compose as shown below).*

### 6. Run the Flask Application Locally

```bash
python app.py
```

Access the frontend dashboard at `http://localhost:5000`.

---

## Containerization with Docker Compose

### 1. Build and Run Containers

Run from the project root:

```bash
docker compose up --build -d
```

This starts:
1. **`mysql` container:** Running MySQL 5.7 on mapped port `3307:3306` with persistent volume `mysql_data`.
2. **`app` container:** Running the Flask web application on port `5000:5000`.

To view app logs:
```bash
docker logs -f inventory-management-system-app-1
```

### 2. Verify Application and Endpoints

- Open **`http://localhost:5000`** in your browser to interact with the Dashboard.
- Access **`http://localhost:5000/products`** to view or add products.
- Access **`http://localhost:5000/place-order`** to create orders.
- Access **`http://localhost:5000/reports`** to inspect the reports.
- Access **`http://localhost:5000/api/report`** to verify JSON payloads.

---

## Kubernetes Deployment

### 1. Prerequisites for Kubernetes
- Docker Desktop with Kubernetes enabled or a cluster such as Minikube.
- `kubectl` CLI installed and configured.

### 2. Using Local Images in Kubernetes

Build the application image:
```bash
docker build -t inventory-app:latest .
```

### 3. Kubernetes YAML Configurations

MySQL Deployment & Service (`mysql-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:5.7
        env:
          - name: MYSQL_ROOT_PASSWORD
            value: "abcde"
          - name: MYSQL_DATABASE
            value: "inventory_db"
          - name: MYSQL_USER
            value: "inventory_user"
          - name: MYSQL_PASSWORD
            value: "inventory_pass"
        ports:
        - containerPort: 3306
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
spec:
  selector:
    app: mysql
  ports:
    - port: 3306
      targetPort: 3306
  clusterIP: None
```

Flask App Deployment & Service (`inventory-app-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-app-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-app
  template:
    metadata:
      labels:
        app: inventory-app
    spec:
      containers:
      - name: inventory-app
        image: inventory-app:latest
        imagePullPolicy: IfNotPresent
        env:
          - name: DB_USER
            value: "inventory_user"
          - name: DB_PASSWORD
            value: "inventory_pass"
          - name: DB_HOST
            value: "mysql-service"
          - name: DB_PORT
            value: "3306"
          - name: DB_NAME
            value: "inventory_db"
          - name: SECRET_KEY
            value: "your_secret_key"
        ports:
          - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: inventory-app-service
spec:
  selector:
    app: inventory-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
  type: LoadBalancer
```

### 4. Deploying to Kubernetes

Apply manifests:
```bash
kubectl apply -f mysql-deployment.yaml
kubectl apply -f inventory-app-deployment.yaml
```

Check status:
```bash
kubectl get pods
kubectl get svc
```

Access application via port-forwarding if LoadBalancer external IP is pending:
```bash
kubectl port-forward svc/inventory-app-service 5000:80
```

---

## Troubleshooting

- **DNS or Network Issues During Build:**
  ```bash
  DOCKER_BUILDKIT=0 docker compose up --build
  ```
- **Database Connection Port Distinction:**
  - When running Flask **locally on host machine**: connect using `DB_HOST=127.0.0.1` and `DB_PORT=3307`.
  - When running inside **Docker Compose network**: connect using `DB_HOST=mysql` and `DB_PORT=3306`.
- **Frontend Assets & JavaScript:**
  - Lucide icons load from CDN via `https://unpkg.com/lucide@latest/dist/umd/lucide.min.js`.
  - If icons fail to display in offline environments, download `lucide.min.js` and serve it directly from `static/js/`.
