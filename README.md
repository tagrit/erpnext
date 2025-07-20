# Tagrit ERPNEXT Docker Setup

Welcome to the Tagrit ERPNEXT Docker Setup! Below are guides to help you manage sites, containers, and more in a Dockerized Frappe and ERPNext environment.

## Table of Contents

- [Production Setup](#production-setup)
- [Development Setup](#development-setup)
- [Docker Management](#docker-management)
- [Ports in Use](#ports-in-use)

---

## Production Setup

This guide covers setting up Tagrit ERP in a production environment with Docker.

### Setup

#### Under Development 

### Site Management

#### Create a Site

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



