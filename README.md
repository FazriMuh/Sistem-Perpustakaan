# Sistem Perpustakaan
Skill Test Gefami

## Installation

### Setting Up Virtual Environment (Optional)

To create and activate a virtual environment, run the following commands:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Unix/Mac
source venv/bin/activate  

# For Windows
venv\Scripts\activate  
```

### Package Installation

To install all the required packages, use the following command:

```bash
pip install Flask
```

### Project Structure

After downloading this repository, ensure the folder structure looks like this, with the project folder next to the `venv` folder:

```
/venv
/your_project
│
├── /data
│   ├── user.csv
│   ├── buku.csv
│   └── pinjaman.csv
│
├── /templates
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── add_book.html
│
├── /static
│   └── Image
│       └── front-image3.png
│
└── app.py
```

## Running the Application

To run the application, use the following command in your terminal:

```bash
python app.py
```

## Accessing the Admin Dashboard

To access the admin dashboard, follow these steps:

1. Make sure your application is running. You should see an endpoint like `http://127.0.0.1:5000` in your terminal.
   
2. In your web browser, enter the following URL: `http://127.0.0.1:5000/dashboard`.

This will direct you to the admin dashboard of your application.
