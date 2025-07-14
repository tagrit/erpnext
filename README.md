# 🐳 Tagrit Frappe Docker Dev Setup Guide

## 📌 Prerequisites

Before starting, ensure your development environment meets the following requirements:

- **OS:** Linux/macOS/WSL
- **Docker:** [Installed](https://docs.docker.com/get-docker/)
- **Docker Compose:** [Installed](https://docs.docker.com/compose/install/)

## 🚀 Installation Steps

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/tagrit/frappe_docker.git
cd frappe_docker
```

### 2️⃣ Start the Development Environment

Use the provided script to set up and start the development environment:

```bash
./start.sh dev
```

This command will:
- Build required Docker images
- Set up the Frappe bench and environment
- Launch containers for backend, frontend, database, etc.

### 3️⃣ Access the Application

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

## 🛠️ Customizing the Code

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

## 🧪 Useful Development Commands

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

## 🔑 Default Admin Credentials

| **Field**   | **Value**         |
|------------|-------------------|
| **Username**  | `Administrator`     |
| **Password** | `admin` *(or set during site install)* |

---

## 🙌 Contribution

We welcome contributions from the community!

1. Fork the repo
2. Create your feature branch: `git checkout -b ft-your-feature`
3. Commit your changes: `git commit -m 'Add cool feature'`
4. Push to the branch: `git push origin ft-your-feature`
5. Open a pull request ✅

Happy coding with Tagrit + Frappe! 🚀
