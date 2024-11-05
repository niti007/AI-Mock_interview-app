# Resource Recommender

The Resource Recommender is a Python application that generates personalized recommendations for learning resources based on a user's resume information, job description, and interview performance. It uses natural language processing techniques to analyze the provided data and suggest relevant resources for technical, behavioral, and competency-based interviews.

## Features

1. **Resume and Job Description Parsing**: The application can parse and extract key information from resumes (in PDF or DOCX format) and job descriptions, including skills, experience, education, and job requirements.

2. **Interview Performance Analysis**: The application can analyze the user's interview performance, identify weak areas, and recommend resources to address those areas.

3. **Personalized Resource Recommendations**: Based on the parsed data and the user's performance, the application generates a list of recommended resources, categorized by priority, skill development, interview preparation, and additional resources.

4. **Flexible Question Generation**: The application can generate technical, behavioral, competency-based, and general interview questions based on the provided resume information and job description.

5. **Audio Transcription**: The application can record audio from the user's microphone and transcribe the content using the Whisper speech recognition model.

## Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the main application:
   ```
   python app.py
   ```

3. Follow the on-screen instructions to provide your resume, job description, and interview performance data.

4. The application will generate personalized resource recommendations and interview questions based on the provided information.

## Architecture

The Resource Recommender is built using the following components:

1. **CVParser**: Responsible for parsing resume information (PDF or DOCX) and extracting relevant details such as skills, experience, education, and contact information.

2. **JobDescriptionParser**: Parses job descriptions and extracts required skills, responsibilities, and qualifications.

3. **ResourceRecommender**: Analyzes the parsed resume and job description data, along with the user's interview performance, to generate personalized resource recommendations.

4. **QuestionGenerator**: Generates technical, behavioral, competency-based, and general interview questions based on the parsed data.

5. **AudioHandler**: Handles audio recording and transcription using the Whisper speech recognition model.

6. **Streamlit UI**: Provides a user-friendly interface for the application.

## Contributing

Contributions to the Resource Recommender are welcome! If you find any issues or have suggestions for improvements, feel free to submit a pull request or open an issue.

## License

This project is licensed under the [MIT License](LICENSE).
