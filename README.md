# Crime-Record-Management-System

In the realm of public safety and justice, efficient crime management is more crucial than ever. We're thrilled to introduce our state-of-the-art solution, the Crime Record Management System (CRMS), engineered to transform the way law enforcement agencies manage crime data. This system aims to streamline interactions between citizens and police officers, ensuring efficient FIR (First Information Report) processing and charge sheet management.

---

## 🌟 Technologies Employed:

- Frontend: HTML5, CSS, EJS
- Backend: Django
- Database: MySQL
- Python libraries: Seaborn, Matplotlib

---

## 🔹 Features:

- **FIR Registration**: Citizens can log in to register FIRs, which then require acceptance from a police officer through their dedicated login.
- **Charge Sheet Management**: Once an FIR is accepted, the process moves to charge sheet preparation. Citizens receive updates on the status of their charge sheet – whether it’s still incomplete or completed and viewable.
- **User and Officer Profiles**: Both citizens and officers can edit their profiles, change passwords, and receive notifications about updates.
- **Seamless Interaction**: Facilitates smooth communication and updates between the accused and the police officer.

This project ensures transparency and efficiency in handling crime reports, benefiting both the public and law enforcement.

---

## 🧑💻 Team Members:

- Pranita Bobade
- Chaitanya Thakre
- Kaveri Aher


# How to Use

### 1. Set Up Your MySQL Database

1. Open your MySQL client.
2. Create a new database:

    ```sql
    CREATE DATABASE crime_data;
    ```

### 2. Connect the Database with Django

1. Open the settings.py file in the Django project.
2. Configure the database settings to connect to your MySQL database. For example:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'crime_data',
            'USER': 'your_mysql_username',
            'PASSWORD': 'your_mysql_password',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    ```

### 3. Run the Django Development Server

1. Open terminal and navigate to the directory containing manage.py.
2. Run the server using the following command:

    ```bash
    python manage.py runserver
    ```

### 4. Access the Application

1. Open your web browser.
2. Navigate to the local host URL:

    ```
    http://127.0.0.1:8000/
    ```
