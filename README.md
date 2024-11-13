# Formulate
### An AI-powered solution for automated survey generation, training needs analysis, and personalized learning recommendations. Formulate streamlines training customization by transforming survey insights into actionable growth, enhancing efficiency and engagement in skill development programs. This application allows admins to create customizable surveys, collect responses, and generate data-driven insights and recommendations, ideal for educational and corporate training environments.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Folder Structure](#folder-structure)
3. [Features](#features)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Environment Configuration](#environment-configuration)
5. [Usage](#usage)
   - [Admin Interface](#admin-interface)
   - [Trainee Interface](#trainee-interface)
6. [Technical Details](#technical-details)
   - [Database](#database)
   - [AI Model Integration](#ai-model-integration)
7. [Contributing](#contributing)
8. [License](#license)

---

## Project Overview

Formulate simplifies the survey lifecycle for training assessments. The platform allows administrators to create surveys, analyze responses, and derive actionable insights. Integrated with advanced AI models for recommendations, Formulate helps optimize content based on feedback.

---

## Folder Structure

The project is organized into functional modules as follows:

```plaintext
Formulate/
├── admin_dashboard/               # Core logic for admin functionalities
│   ├── survey_management.py       # Creating and managing surveys
│   ├── survey_recommendations.py  # AI-powered recommendations module
│   ├── survey_reports.py          # Report generation and display
│   ├── survey_responses.py        # Response management
├── ai/                            # AI-related functionalities and configurations
│   ├── ai_service.py              # Main service handling AI recommendations
│   ├── config.py                  # AI model configurations
│   ├── generate.py                # AI model generation and setup
├── Images/                        # Images used in the application interface
├── pages/                         # Page-specific components
│   ├── 1_trainee_form.py          # Survey form for trainees
├── responses/                     # Stores survey responses
├── survey_jsons/                  # JSON files for survey configurations
├── utils/                         # Utility scripts and helper functions
│   ├── auth.py                    # Authentication and access control
│   ├── create_database_tables.py  # Database table setup script
│   ├── dummy_responses.xlsx       # Sample response data
├── .gitignore                     # Git ignore file
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── streamlit_app.py               # Main Streamlit application file
```

The main file for loading the application in Streamlit is streamlit_app.py. This file serves as the entry point for running the application and initializing the Streamlit interface. All other code components and functionalities are to be built and organized separately, ensuring modularity and ease of development.

---

## Features

- **Survey Management**: Create, customize, and manage training surveys.
- **Response Collection**: Collect structured feedback from trainees.
- **AI-Powered Recommendations**: Generate data-driven suggestions for content improvement using AI.
- **Comprehensive Reports**: Analyze survey outcomes with balanced feedback.
- **User-Friendly Interface**: Intuitive UI built with Streamlit for easy navigation.

---

## Getting Started

### Prerequisites

- **Python 3.8 or above**: Required for running the application.
- **Streamlit**: The project uses Streamlit as the main web framework.
- **MySQL**: For storing survey data and responses.
- **OpenAI API Key**: Necessary for AI-based recommendations.

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/formulate.git
   cd formulate
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration

1. **Configure Environment Variables**

   Create a `.env` file in the root directory with the necessary environment variables, including OpenAI API and database connection details.

   Example `.env` file:

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   MYSQL_HOST=your_mysql_host
   MYSQL_USER=your_mysql_user
   MYSQL_SECRET_KEY=your_mysql_password
   MYSQL_DATABASE=your_mysql_database
   ```

2. **Database Setup**

   Run `create_database_tables.py` in the `utils/` directory to set up the database schema.

   ```bash
   python utils/create_database_tables.py
   ```

3. **Run the Application**

   Start the Streamlit application:

   ```bash
   streamlit run streamlit_app.py
   ```

   The app will be accessible at `http://localhost:8501`.

---

## Usage

### Admin Interface

1. **Login**: Access the admin interface by logging in.
2. **Survey Creation**: Go to the Survey Management section to create new surveys.
3. **View Responses**: Check survey responses in the Survey Responses section.
4. **Reports and Recommendations**: Review generated recommendations and analyze reports based on trainee feedback.

### Trainee Interface

1. **Survey Completion**: Trainees access the survey form through a unique link, answer questions, and submit their responses.
2. **Submit**: Responses are stored and accessible to admins for review.

---

## Technical Details

### Database

Formulate uses a MySQL database to store survey data, trainee responses, and metadata. Run `create_database_tables.py` in the `utils/` directory to initialize the database schema.

### AI Model Integration

The platform uses an OpenAI model (configured in `GptModels` in the backend) to generate recommendations based on survey responses. The AI configuration is set in the `ai/` directory, with `ai_service.py` handling interactions with OpenAI.

---

## Contributing

We welcome contributions to improve Formulate. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`feature/your-feature-name`).
3. Commit your changes.
4. Push your branch and create a pull request.

---

## License

This project is licensed under the MIT License.

---

For assistance or to report issues, please contact the project maintainers or open an issue on GitHub. Thank you for using Formulate!