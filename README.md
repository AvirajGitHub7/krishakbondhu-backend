# KrishakBondhu Backend API

The backend for the KrishakBondhu platform is a robust, asynchronous REST API built with FastAPI. It powers both the mobile Farmer App and the web-based Admin Panel, providing data management, authentication, and integration with advanced AI models for crop disease detection.

## About the Project

This service is the central nervous system of KrishakBondhu. It handles all business logic, database interactions, and third-party API integrations. Key capabilities include:

*   **Machine Learning Integration**: Direct integration with HuggingFace models for real-time analysis and prediction of crop diseases from uploaded images.
*   **Media Management**: Secure, direct-to-cloud image uploads using Cloudinary.
*   **Secure Authentication**: Role-based access control (Admin, Expert, User) utilizing JSON Web Tokens (JWT).
*   **Database Connectivity**: Asynchronous data persistence using Motor (MongoDB Async Driver).
*   **Comprehensive Endpoints**: Dedicated routers for users, community posts, expert requests, AI predictions, and administrative management.

## Technology Stack

*   **Framework**: FastAPI
*   **Server**: Uvicorn
*   **Database**: MongoDB Atlas (Motor Async Client)
*   **Authentication**: Passlib, Bcrypt, Python-JOSE
*   **Machine Learning**: PyTorch, Transformers (HuggingFace)
*   **Media**: Cloudinary

## Prerequisites

*   Python (v3.10 or higher recommended)
*   A running MongoDB instance (Local or MongoDB Atlas)
*   Cloudinary Account (for image uploads)

## Installation and Setup

1.  **Navigate to the project directory:**
    ```bash
    cd KrishakBondhu/backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root of the `backend` directory. See `.env.example` for a template of the required keys, including MongoDB connection strings and Cloudinary API credentials.

5.  **Start the server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can explore and test the endpoints at:
*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

*   `app/api/`: API route definitions and endpoint handlers.
*   `app/core/`: Application configuration and security utilities.
*   `app/db/`: MongoDB connection setup and management.
*   `app/models/`: Pydantic data models for request/response validation.
*   `app/services/`: Core business logic and database interactions.
*   `app/ml/`: Machine learning model initialization and prediction logic.
