# Forex Watcher Web Application

This is a simple web application built with Django that allows users to monitor real-time forex exchange rates for UGX-USD currency pairs and subsequently more. It features an embedded TradingView chart, real-time rate cards, and a client-side alert system.

## Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.x** (preferably Python 3.9 or higher)
*   **pip** (Python package installer)

### Installation

1.  **Access the project:**
    Download / clone the project, un-ZIP the file and extract its contents to your desired directory.

2.  **Navigate to the project directory:**
    Open your terminal or command prompt and navigate to the root directory of the extracted project:
    ```bash
    cd path/to/your/forex_watcher
    ```

3.  **Create a virtual environment (recommended):**
    It's good practice to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    ```

4.  **Activate the virtual environment:**
    *   **On Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

5.  **Install dependencies:**
    Install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Apply database migrations:**
    This will set up the necessary database tables for the project.
    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser:**
    You'll need a superuser account to log in and access the application. Follow the prompts to create a username, email (optional), and password.
    ```bash
    python manage.py createsuperuser
    ```

### Running the Application

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:8000/`.
    You will be redirected to the login page. Use the superuser credentials you created earlier to log in.

## Features

*   **Real-time Forex Rates:** Displays current exchange, buy, and sell rates, along with 24-hour high and low for UGX-USD.
*   **Interactive Chart:** Embedded TradingView widget for comprehensive forex data visualization.
*   **Client-Side Alerts:** Set custom price alerts (above/below thresholds) with instant notifications.
*   **User Authentication:** Secure login and logout functionality.


## 
***Good luck.***

