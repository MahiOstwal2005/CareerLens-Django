# CareerLens

CareerLens is an AI-powered Resume Analyzer and Application Tracking System (ATS) optimization tool built with Django. It helps job seekers optimize their resumes by analyzing uploaded documents, extracting key information, and scoring them against industry-standard ATS metrics.

## Features

- **Resume Upload & Parsing**: Upload your resume and let the system extract text and key information automatically.
- **ATS Scoring**: Get an instant ATS compatibility score based on formatting, keywords, and content.
- **Keyword Analysis**: Identify matched and missing keywords to better tailor your resume for specific roles.
- **Interactive Dashboard**: Track your resume scores over time, view your health tier (Novice to Top 1%), and get actionable feedback.
- **MongoDB Integration**: Stores detailed analytics and resume data efficiently.
- **User Authentication**: Secure user registration, login, and personalized resume history.

## Technology Stack

- **Backend**: Python, Django
- **Database**: SQLite (Primary), MongoDB (Analytics & Reporting)
- **Frontend**: HTML, CSS, JavaScript (Chart.js for analytics)

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
- Python 3.8 or higher
- MongoDB (running locally or a MongoDB Atlas URI)
- Git

## Installation & Setup

Follow these steps to get your development environment set up:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MahiOstwal/CareerLens-Django.git
   cd CareerLens
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Environment Variables:**
   Create a `.env` file in the root directory and configure your variables (e.g., MongoDB URI, Django Secret Key):
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=careerlens_db
   ```

6. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:8000/`.

## Daily Workflow for Developers

We have provided a helper script to make committing and pushing your daily work easy.

1. Make sure your script is executable:
   ```bash
   chmod +x push_daily.sh
   ```
2. Run the script at the end of your work session:
   ```bash
   ./push_daily.sh
   ```
   *This will automatically add your changes, ask for a commit message, and push to the `main` branch.*

## Contributing

1. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License.
