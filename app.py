import streamlit as st
import os
import tempfile
import asyncio  # Import asyncio for handling async functions
from utils.cv_parser import CVParser
from utils.JD_parser import JobDescriptionParser
from models.question_generator import QuestionGenerator
from models.resource_recommender import ResourceRecommender

# Hardcode your Google API key here
google_api_key = "AIzaSyD4-wE6U-sLPj1ABnkUB9i_ewsoiXM8aHA"  # Replace with your actual API key

def save_uploadedfile(uploadedfile):
    """Save uploaded file to a temporary file and return the path"""
    if uploadedfile is None:
        return None
    try:
        suffix = os.path.splitext(uploadedfile.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploadedfile.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def initialize_session_state():
    """Initialize all session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'upload'
    if 'interview_data' not in st.session_state:
        st.session_state.interview_data = {}
    if 'interview_progress' not in st.session_state:
        st.session_state.interview_progress = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []

def cleanup_temp_files():
    """Clean up temporary files when the session ends"""
    for temp_file in st.session_state.temp_files:
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except Exception as e:
            st.warning(f"Error cleaning up temporary file {temp_file}: {str(e)}")

async def process_documents(cv_temp_path, jd_temp_path, cv_parser, jd_parser):
    """Process the uploaded CV and JD files"""
    st.session_state.interview_data['cv_data'] = cv_parser.parse_cv(cv_temp_path)
    if jd_temp_path:
        st.session_state.interview_data['jd_data'] = jd_parser.parse_job_description(jd_temp_path)

async def main():  # Define main as an async function
    st.set_page_config(
        page_title="AI Mock Interview Assistant",
        page_icon="🎯",
        layout="wide"
    )

    initialize_session_state()

    # Initialize QuestionGenerator with the Google API key
    question_generator = QuestionGenerator(api_key=google_api_key)

    # Sidebar configuration
    with st.sidebar:
        st.title("Interview Setup")
        interview_type = st.selectbox(
            "Select Interview Type",
            ["Competency Based", "Behavioral", "Technical"],
            help="Choose the type of interview you want to practice"
        )

        if interview_type == "Technical":
            technical_stack = st.multiselect(
                "Select Technical Stack",
                ["Python", "JavaScript", "Java", "React", "Node.js", "SQL"],
                help="Choose technologies you want to be interviewed on"
            )
            st.session_state.interview_data['technical_stack'] = technical_stack  # Store selected stack in session state

    st.title("AI Mock Interview Assistant")

    if st.session_state.current_step == 'upload':
        st.header("Upload Documents")

        with st.expander("📌 Tips for better results", expanded=True):
            st.markdown(""" 
            - Ensure your CV is up-to-date 
            - Include relevant skills and experience 
            - For technical interviews, highlight your project experience 
            """)

        cv_file = st.file_uploader("Upload your CV (Required)", type=["pdf", "docx"])
        jd_file = st.file_uploader("Upload Job Description (Optional)", type=["pdf", "docx", "txt"])

        if cv_file is not None:
            cv_parser = CVParser()
            jd_parser = JobDescriptionParser()

            if st.button("Process Documents", type="primary"):
                with st.spinner("Processing your documents..."):
                    try:
                        # Save uploaded files to temporary files
                        cv_temp_path = save_uploadedfile(cv_file)
                        if cv_temp_path:
                            st.session_state.temp_files.append(cv_temp_path)

                            jd_temp_path = save_uploadedfile(jd_file) if jd_file else None
                            if jd_temp_path:
                                st.session_state.temp_files.append(jd_temp_path)

                            # Now await the document processing
                            await process_documents(cv_temp_path, jd_temp_path, cv_parser, jd_parser)

                            st.session_state.current_step = 'confirm'
                            st.success("Documents processed successfully!")
                            st.experimental_rerun()  # Refresh the UI
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
                        cleanup_temp_files()

    elif st.session_state.current_step == 'confirm':
        st.header("Confirm Interview Setup")

        # Display parsed information
        st.subheader("Parsed Information")
        st.write("Interview Type:", st.session_state.interview_data.get('interview_type', 'Not specified'))
        if 'technical_stack' in st.session_state.interview_data:
            st.write("Technical Stack:", ", ".join(st.session_state.interview_data['technical_stack']))

        # Generate questions when confirmed
        if st.button("Start Interview", type="primary"):
            with st.spinner("Generating interview questions..."):
                # Await question generation in async context
                questions = await question_generator.generate_questions(
                    question_type=interview_type,
                    resume_info=st.session_state.interview_data.get('cv_data'),
                    job_description=st.session_state.interview_data.get('jd_data'),
                    technical_stack=st.session_state.interview_data.get('technical_stack')
                )

                if questions:
                    st.session_state.questions = questions
                    st.session_state.current_step = 'interview'
                    st.experimental_rerun()  # Refresh to display interview step
                else:
                    st.error("Failed to generate interview questions. Please try again.")

    elif st.session_state.current_step == 'interview':
        st.header("Mock Interview")

        # Display progress
        progress = st.progress(st.session_state.interview_progress)
        st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")

        # Display current question
        if st.session_state.questions:
            current_q = st.session_state.questions[st.session_state.current_question]
            st.subheader(current_q)

            # Get user response
            user_response = st.text_area("Your Answer:", height=150)

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Submit Answer", type="primary"):
                    if user_response:
                        # Save response
                        st.session_state.responses.append({
                            'question': current_q,
                            'response': user_response
                        })

                        # Generate simple feedback
                        feedback = {
                            'clarity': 0.8,  # Placeholder values
                            'relevance': 0.85,
                            'confidence': 0.75,
                            'feedback': "Good response! Consider providing more specific examples."
                        }
                        st.session_state.feedback[st.session_state.current_question] = feedback

                        # Update progress
                        st.session_state.current_question += 1
                        st.session_state.interview_progress = st.session_state.current_question / len(
                            st.session_state.questions)

                        # Check if interview is complete
                        if st.session_state.current_question >= len(st.session_state.questions):
                            st.session_state.current_step = 'summary'

                        # Instead of st.experimental_rerun(), we can call main() directly
                        await main()  # Call the main loop directly
                    else:
                        st.warning("Please provide an answer before proceeding.")

    elif st.session_state.current_step == 'summary':
        st.header("Interview Summary")

        # Display overall performance metrics
        if st.session_state.feedback:
            avg_clarity = sum(f['clarity'] for f in st.session_state.feedback.values()) / len(st.session_state.feedback)
            avg_relevance = sum(f['relevance'] for f in st.session_state.feedback.values()) / len(st.session_state.feedback)
            avg_confidence = sum(f['confidence'] for f in st.session_state.feedback.values()) / len(
                st.session_state.feedback)

            col1, col2, col3 = st.columns(3)
            col1.metric("Average Clarity", f"{avg_clarity:.0%}")
            col2.metric("Average Relevance", f"{avg_relevance:.0%}")
            col3.metric("Average Confidence", f"{avg_confidence:.0%}")

            # Detailed feedback for each question
            st.subheader("Detailed Feedback")
            for idx, response in enumerate(st.session_state.responses):
                with st.expander(f"Question {idx + 1}"):
                    st.write("**Question:**", response['question'])
                    st.write("**Your Response:**", response['response'])
                    feedback = st.session_state.feedback.get(idx, {})
                    st.write("**Feedback:**", feedback.get('feedback', 'No feedback available.'))

            # Recommend resources based on performance
            resource_recommender = ResourceRecommender()
            resources = resource_recommender.recommend_resources(avg_clarity, avg_relevance, avg_confidence)
            if resources:
                st.subheader("Recommended Resources")
                for resource in resources:
                    st.write(resource)

            if st.button("Restart", on_click=lambda: st.session_state.clear()):
                st.session_state.clear()

    cleanup_temp_files()  # Clean up temp files after the session ends

if __name__ == "__main__":
    asyncio.run(main())
