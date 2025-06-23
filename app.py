from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import pandas as pd
from agno.tools import tool
import requests
import os
import fitz 
from dotenv import load_dotenv
import streamlit as st
import json

# Load environment
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        # Read the uploaded file bytes
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

# Agent 1: Resume Analyzer
resume_agent = Agent(
    name="ResumeAgent",
    role="Extracts skills from resume",
    model=Groq(id="qwen/qwen3-32b"),
    instructions="Given a resume, extract skills, education, experience, and certifications in JSON format.",
    show_tool_calls=True,
    markdown=True,
)

# Agent 2: Job Role Analyzer
job_role_analyzer = Agent(
    name="JobRoleAnalyzer",
    role="Suggests suitable job roles based on skills",
    model=Groq(id="qwen/qwen3-32b"),
    instructions="""
You are a career advisor. Given structured skills in JSON format from a resume, suggest 3-5 suitable job roles.
For each job role, include:
1. Job Title
2. Why it's a good fit based on the skills
3. Key technologies or competencies required for the role
Make suggestions relevant Field.
""",
    show_tool_calls=False,
    markdown=True,
)

# Job Searching Agent
job_searching_agent = Agent(
    name="JobSearchingAgent",
    role="Finds job openings online based on provided job titles",
    model=Groq(id="qwen/qwen3-32b"),
    tools=[DuckDuckGoTools()],  # Use DuckDuckGo for search
    instructions="""
You are a job search assistant. You will be given a list of job titles.

For each job title:
- Use your tools to search for recent job openings.
- Focus on job websites like bdjobs.com, linkedin.com, or indeed.com.
- Provide job title and 3-5 job links for each.
- Return result in structured JSON format and Markdown.

Search query format example: "Junior Python Developer site:bdjobs.com OR site:linkedin.com OR site:indeed.com"
""",
    show_tool_calls=True,
    markdown=True,
)

@tool
def estimate_salary(job_title: str, location: str = "Bangladesh") -> dict:
    """
    Estimate salary using RapidAPI based on job title and location.
    """
    if not os.getenv("RAPIDAPI_KEY"):
        return {"job_title": job_title, "error": "RAPIDAPI_KEY not configured"}
    
    url = "https://jsearch.p.rapidapi.com/estimated-salary"
    headers = {
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    }
    params = {
        "job_title": job_title,
        "location": location,
        "location_type": "ANY",
        "years_of_experience": "ALL",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get("estimated_salary", {})
            return {
                "job_title": job_title,
                "location": location,
                "min": data.get("min"),
                "max": data.get("max"),
                "currency": data.get("currency"),
            }
        else:
            return {"job_title": job_title, "error": response.text}
    except Exception as e:
        return {"job_title": job_title, "error": str(e)}

salary_estimator_agent = Agent(
    name="SalaryEstimatorAgent",
    role="Estimates salary for each job title",
    model=Groq(id="qwen/qwen3-32b"),
    tools=[estimate_salary],
    instructions="""
You are a salary estimation assistant. You will be given job titles.

For each job title:
- Call the `estimate_salary` tool.
- Provide job title, estimated salary min-max range, and currency.
- Return the result in a structured JSON and Markdown table.
""",
    show_tool_calls=True,
    markdown=True,
)

@tool
def search_jobs(query: str, page: int = 1, num_pages: int = 1, country: str = "bd", date_posted: str = "all") -> list:
    """
    Search job listings from RapidAPI JSearch.
    """
    if not os.getenv("RAPIDAPI_KEY"):
        return [{"error": "RAPIDAPI_KEY not configured"}]
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    }
    params = {
        "query": query,
        "page": str(page),
        "num_pages": str(num_pages),
        "country": country,
        "date_posted": date_posted,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json().get("data", [])
            results = []
            for job in data:
                results.append({
                    "title": job.get("job_title"),
                    "company": job.get("employer_name"),
                    "location": job.get("job_city"),
                    "url": job.get("job_apply_link"),
                    "posted": job.get("job_posted_at_datetime_utc")
                })
            return results
        else:
            return [{"error": response.text}]
    except Exception as e:
        return [{"error": str(e)}]

job_search_agent = Agent(
    name="JobSearchAgent",
    role="Searches for jobs based on job title and location",
    model=Groq(id="qwen/qwen3-32b"),
    tools=[search_jobs],
    instructions="""
You are a job search agent. You will receive job titles and locations.

For each title and location:
- Call `search_jobs` tool with query like "python developer jobs in Dhaka".
- Return top job listings with title, company, location, apply link, and post date.
- Format response as a Markdown table and also return structured JSON.
""",
    show_tool_calls=True,
    markdown=True,
)

# Multi-Agent Orchestrator
multi_agent = Agent(
    team=[resume_agent, job_role_analyzer, job_search_agent],
    model=Groq(id="qwen/qwen3-32b"),
    instructions=[
        "Use each agent for their assigned task.",
        "Present the final result in markdown and JSON format.",
    ],
    show_tool_calls=True,
    markdown=True,
)

# ---- Streamlit UI ----
st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .result-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🧠 Smart Resume Career Advisor</h1>', unsafe_allow_html=True)

# Create two columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type="pdf")
    custom_prompt = st.text_area(
        "🔍 Enter a Prompt", 
        placeholder="Example: Suggest me job roles based on my resume.",
        height=100
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 📋 How it works:")
    st.markdown("""
    1. **Upload** your resume (PDF format)
    2. **Enter** specific requirements or preferences
    3. **Click** 'Run Analysis' to get AI-powered insights
    4. **View** personalized job recommendations
    """)
    
    st.markdown("### 🚀 Features:")
    st.markdown("""
    - **Skills extraction** from your resume
    - **Job role suggestions** based on your profile
    - **Live job search** from multiple platforms
    - **Salary estimation** for recommended roles
    """)

# Main analysis section
if uploaded_file and custom_prompt:
    if st.button("🚀 Run Analysis", type="primary"):
        with st.spinner("⏳ Analyzing your resume and finding job matches..."):
            try:
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if not resume_text:
                    st.error("❌ Failed to extract text from the uploaded PDF. Please try again.")
                    st.stop()
                
                # Show preview of extracted text
                with st.expander("📝 Preview of Extracted Text"):
                    st.text_area("Resume Text", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200)
                
                # Run multi-agent analysis
                st.info("🤖 Running AI analysis...")
                
                # Use run() instead of print_response() to get the response object
                response = multi_agent.run(f"extract skills {resume_text} from it. and follow the instructions: {custom_prompt}")
                
                # Display results
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown("## 🧾 Analysis Results")
                
                # Check if response has content
                if hasattr(response, 'content') and response.content:
                    # Display the markdown if available
                    if hasattr(response, 'markdown') and response.markdown:
                        st.markdown(response.markdown)
                    else:
                        # Fallback to content
                        st.markdown(response.content)
                    
                    # Show JSON data
                    with st.expander("🔎 View Raw Data (JSON)"):
                        try:
                            # Try to parse as JSON
                            json_data = json.loads(response.content) if isinstance(response.content, str) else response.content
                            st.json(json_data)
                        except:
                            # If not JSON, show as text
                            st.text(response.content)
                
                else:
                    st.warning("⚠️ No response received from the AI agents. Please try again.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Additional features section
                st.markdown("---")
                st.markdown("## 🎯 Next Steps")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💰 Get Salary Estimates"):
                        st.info("Feature coming soon! Salary estimation for recommended roles.")
                
                with col2:
                    if st.button("🔍 Search More Jobs"):
                        st.info("Feature coming soon! Extended job search with more filters.")
                
                with col3:
                    if st.button("📊 Skills Gap Analysis"):
                        st.info("Feature coming soon! Identify skills to improve for better job matches.")
                
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {str(e)}")
                st.markdown("Please try again or check your API keys if the issue persists.")
                
                # Show error details in expandable section
                with st.expander("🔧 Error Details"):
                    st.code(str(e))

elif uploaded_file and not custom_prompt:
    st.info("💡 Please enter a prompt to describe what you'd like to know about your resume.")
    st.markdown("**Example prompts:**")
    st.markdown("- Suggest me job roles based on my resume")
    st.markdown("- Find remote work opportunities for my skills")
    st.markdown("- What are the highest paying jobs for my background?")
    st.markdown("- Show me entry-level positions in my field")

elif not uploaded_file:
    st.info("👆 Please upload your resume (PDF format) to get started!")
    
    # Show demo section
    with st.expander("🎬 See Demo"):
        st.markdown("""
        **This AI-powered career advisor will help you:**
        
        - **Extract key skills** and experience from your resume
        - **Suggest relevant job roles** based on your background
        - **Find active job listings** from multiple job boards
        - **Estimate salary ranges** for different positions
        - **Provide personalized career guidance**
        
        Simply upload your resume and describe what you're looking for!
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>🤖 Powered by AI Agents | 📊 Smart Career Analysis | 🚀 Built with Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)