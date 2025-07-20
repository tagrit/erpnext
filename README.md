# 🚀 Tagrit ERPNEXT Docker Management

Welcome to the **Tagrit ERPNEXT Docker** setup! This guide will help you manage sites, Docker containers, and development/production environments in a clean and automated way.

---

## 📚 Table of Contents

- [📦 Production Setup](#-production-setup)
  - [⚙️ Setup](#️-setup)
  - [🌐 Site Management](#-site-management)
- [👨‍💻 Development Setup](#-development-setup)
- [🐳 Docker Management](#-docker-management)
- [📡 Ports in Use](#-ports-in-use)

---

## 📦 Production Setup

This guide covers how to set up and manage sites in a production environment using Docker and Frappe.

### ⚙️ Setup

_This section is under development — to be updated soon._

---

### 🌐 Site Management

#### ✅ Create a New Site

To create a new site on your production server:

1. **SSH into the server**

   Access your production server via SSH:

 ```bash
 ssh user@your-production-server
  ```

2 **Run the `create_site` Command**

Run the site creation script:

```bash
create_site
```
#### Follow the Prompts

- **Domain name**  
  Enter a domain in the format `*.tagrit.com`, for example:  
  `doc.tagrit.com`

- **Port number**  
  Enter the port where the site will run.  
  To check used and available ports, run:

  ```bash
  ports_in_use
  ```
- **Apps to install**  
  Enter a comma-separated list of apps to install, such as:

  ```text
  erpnext,hrms,payments
  ```
- **Press Enter and let the script handle the rest.**

#### ❌ Drop a Site

To remove a site completely from your production setup:

```bash
drop_site doc.tagrit.com
```
- **Press Enter and let the script handle the rest. Once done you will get a confirmation message**

✅ Site doc.tagrit.com has been fully removed and system restarted.

#### 📡 Ports in Use

You can check which ports are currently assigned to Frappe frontend containers using:

```bash
ports_in_use
```
- **Press Enter and let the script handle the rest. Once done you will be able to view currently used ports**

🔍 Ports currently used by Frappe frontend containers:

| PORT  | SITE          |
|-------|---------------|
| 8080  | 1             |
| 8081  | default       |
| 8085  | clientportal  |
| 8086  | sandbox       |

✅ **Suggested next available port: 8087**




## 👨‍💻 Development Setup

This section helps you spin up a local Frappe + ERPNext environment using Docker.

### 📌 Prerequisites

Before starting, ensure your development environment meets the following requirements:

- **OS:** Linux/macOS/WSL
- **Docker:** [Installed](https://docs.docker.com/get-docker/)
- **Docker Compose:** [Installed](https://docs.docker.com/compose/install/)

## #🚀 Installation Steps

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/tagrit/frappe_docker.git
cd frappe_docker
```

#### 2️⃣ Start the Development Environment

Use the provided script to set up and start the development environment:

```bash
./start.sh dev
```

This command will:
- Build required Docker images
- Set up the Frappe bench and environment
- Launch containers for backend, frontend, database, etc.

#### 3️⃣ Access the Application

Once the setup is complete, open your browser and visit:

👉 [http://app.tagrit.com:8000](http://app.tagrit.com:8000)

> 🔒 **Note:** Ensure `app.tagrit.com` points to `127.0.0.1` in your `/etc/hosts` file:
>
> ```bash
> sudo nano /etc/hosts
> ```
> Add the following line:
> ```
> 127.0.0.1 app.tagrit.com
> ```

You can also access other frontends like:

👉 [http://kevin.tagrit.com:8082](http://kevin.tagrit.com:8082)

---

### 🛠️ Customizing the Code

Your codebase can be customized in these directories:

- `apps/` – contains Frappe and custom apps
- `sites/` – contains site configurations and files

After making code or config changes, restart the containers:

```bash
docker compose restart
```

Or restart only the backend for faster feedback:

```bash
docker compose restart backend
```

---

### 🧪 Useful Development Commands

To interact with the environment:

```bash
# Access the backend container
docker exec -it frappe-docker-backend-1 bash

# Restart bench inside the container
bench restart

# Run Frappe commands
bench --site your-site-name console
bench --site your-site-name migrate
```

---

### 🔑 Default Admin Credentials

| **Field**   | **Value**         |
|------------|-------------------|
| **Username**  | `Administrator`     |
| **Password** | `admin` *(or set during site install)* |

---

### 🙌 Contribution

We welcome contributions from the community!

1. Fork the repo
2. Create your feature branch: `git checkout -b ft-your-feature`
3. Commit your changes: `git commit -m 'Add cool feature'`
4. Push to the branch: `git push origin ft-your-feature`
5. Open a pull request ✅

Happy coding with Tagrit + Frappe! 🚀




