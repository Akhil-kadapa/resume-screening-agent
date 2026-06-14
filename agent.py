import google.generativeai as genai #importing google generative ai as genai which can generate the insights for the data
import json #importing json for converting python dictionary to json text and vice versa
import csv # importing csv to make a spreadsheet for the results
import PyPDF2 #for reading pdf files
from pathlib import Path # path helps to work with files and folders in computer

#Step 1: setting up API  key 
API_KEY = "your-api-key_here"# Using GEMINI KEY

genai.configure(api_key=API_KEY) #configuring genai model 
model = genai.GenerativeModel("gemini-2.5-flash")# using gemini-2.5-flash

# Step 2: defining a function named as extract_text_from_pdf to read the text in the pdf
def extract_text_from_pdf(pdf_path):#using pdf_path as the input for the function
    """Reads a PDF file and returns all the text inside it.""" #using docstring to describe the function work
    text = "" #create a empty bucket later use the data from the files
    with open(pdf_path, "rb") as file:#using pdf_path open them as file rb is used for read binary text which is supported by pdf format
        reader = PyPDF2.PdfReader(file)#reads the pdf file
        for page in reader.pages:#using for loop it reads all the pages in the pdf
            text += page.extract_text()#extract all the text to the text bucket
    return text# returns the bucket

# STEP 3: Screen a single resume using Gemini 
def screen_resume(resume_text, job_description):#using function to screen the resume calling with screen_resume function name and we use reume_text and job_description as the input to gemini
    """
    Sends the resume + job description to Gemini.
    Gemini returns a structured score and analysis.
    """

    prompt = f"""You are an expert HR recruiter and talent acquisition specialist.
Your job is to screen resumes against job descriptions fairly and thoroughly.

You MUST respond with ONLY a valid JSON object.
No extra text before or after. Just the JSON.

The JSON must follow this exact format:
{{
  "candidate_name": "Full name from resume",
  "overall_score": 75,
  "grade": "B",
  "skills_match": {{
    "score": 80,
    "matched_skills": ["Python", "Machine Learning"],
    "missing_skills": ["Docker", "AWS"]
  }},
  "experience_match": {{
    "score": 70,
    "summary": "2 years experience, role requires 3-5 years"
  }},
  "education_match": {{
    "score": 90,
    "summary": "Masters in AI - strong match"
  }},
  "strengths": [
    "Strong Python skills",
    "Relevant ML project experience"
  ],
  "weaknesses": [
    "Limited industry experience",
    "No cloud platform experience"
  ],
  "recommendation": "MAYBE",
  "recommendation_reason": "Strong technical skills but lacks experience"
}}

Scoring rules:
- overall_score: 0-100 (weighted average of all categories)
- grade: A (90-100), B (75-89), C (60-74), D (below 60)
- recommendation: "YES" (score >= 75), "MAYBE" (score 55-74), "NO" (score < 55)

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Return ONLY the JSON evaluation. No other text.""" #here we give prompt to the gemini on which metrics the resume should be evaluated and ask it to return the data in a json formate and no other one

    # Send to Gemini API
    response = model.generate_content(prompt) #after the prompt it was sent to gemini api. here we use response variable to store the gemini model generated data by using the prompt we gave

    # Get the text response and clean it
    result_text = response.text.strip()#using the response data and clean it using strip function and store it in result_text variable

    # Remove markdown code blocks if Gemini adds them
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]#we remove mark down codes if gemini adds them by usinbg split function by using index numbers
        if result_text.startswith("json"):
            result_text = result_text[4:]#if result_text start with "json" we use 4: to remove those

    # Convert JSON text to Python dictionary
    result = json.loads(result_text.strip())
    return result#convert json text to python dictionary we is readable


# STEP 4: Screen multiple resumes and rank them
def screen_multiple_resumes(resume_folder, job_description):# Screening multiple resumes at once
    """
    Goes through all PDF resumes in a folder,
    screens each one, and returns a ranked list.
    """
    results = [] # empty list to store all candidate evaluation
    resume_folder = Path(resume_folder)#by using path library which is used to work folders we can get to resume folder where we save all the pdf resumes that are need to be screened

    # Find all PDF files in the folder
    pdf_files = list(resume_folder.glob("*.pdf"))#by using *.pdf wildcard pattern list out all the resumes that are ending with .pdf

    if not pdf_files:
        print("❌ No PDF files found in the folder!")#if no resumes found then print no pdf found
        return []

    print(f"📄 Found {len(pdf_files)} resume(s) to screen...\n")# f string is used to add strings and len function which tells the number of resumes found

    for pdf_file in pdf_files:
        print(f"🔍 Screening: {pdf_file.name}")

        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(pdf_file)

            # Screen with Gemini
            evaluation = screen_resume(resume_text, job_description)

            # Add the filename to results
            evaluation["file"] = pdf_file.name
            results.append(evaluation)

            print(f"   ✅ Score: {evaluation['overall_score']}/100 | Grade: {evaluation['grade']} | {evaluation['recommendation']}\n")

        except Exception as e:
            print(f"   ❌ Error screening {pdf_file.name}: {e}\n")

    # Sort by score (highest first)
    results.sort(key=lambda x: x["overall_score"], reverse=True)#we used lambda function to sort the outputs and arrange them in descending order by using reverse=true

    return results


# STEP 5: Save results to a CSV report
def save_report(results, output_file="screening_report.csv"):#save all the results in the csv file in a spredsheet which makes easy to understand
    """Saves all candidate results to a CSV file."""

    if not results:
        print("No results to save.")
        return

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header row
        writer.writerow([
            "Rank", "Candidate Name", "File", "Overall Score", "Grade",
            "Skills Score", "Experience Score", "Education Score",
            "Matched Skills", "Missing Skills",
            "Strengths", "Weaknesses",
            "Recommendation", "Reason"
        ])

        # Data rows
        for rank, result in enumerate(results, 1):
            writer.writerow([
                rank,
                result.get("candidate_name", "Unknown"),
                result.get("file", ""),
                result.get("overall_score", 0),
                result.get("grade", ""),
                result.get("skills_match", {}).get("score", 0),
                result.get("experience_match", {}).get("score", 0),
                result.get("education_match", {}).get("score", 0),
                ", ".join(result.get("skills_match", {}).get("matched_skills", [])),
                ", ".join(result.get("skills_match", {}).get("missing_skills", [])),
                " | ".join(result.get("strengths", [])),
                " | ".join(result.get("weaknesses", [])),
                result.get("recommendation", ""),
                result.get("recommendation_reason", "")
            ])

    print(f"📊 Report saved to: {output_file}")


# STEP 6: Print a nice summary in the terminal 
def print_summary(results):#now we make a summary of our report for the user to understand better in the terminal
    """Prints a clean ranked summary to the terminal."""
    print("\n" + "="*60)
    print("         📋 CANDIDATE RANKING REPORT")
    print("="*60)

    for rank, result in enumerate(results, 1):
        recommendation = result.get("recommendation", "")#we use recommendation parameter in order to recommend the candidate based on the results we get

        if recommendation == "YES":
            icon = "🟢"
        elif recommendation == "MAYBE":
            icon = "🟡"
        else:
            icon = "🔴"

        print(f"\n{icon} Rank #{rank}: {result.get('candidate_name', 'Unknown')}")
        print(f"   Score:          {result.get('overall_score', 0)}/100 (Grade: {result.get('grade', '')})")
        print(f"   Recommendation: {recommendation}")
        print(f"   Reason:         {result.get('recommendation_reason', '')}")
        print(f"   Skills Match:   {result.get('skills_match', {}).get('score', 0)}/100")
        print(f"   Matched Skills: {', '.join(result.get('skills_match', {}).get('matched_skills', []))}")
        print(f"   Missing Skills: {', '.join(result.get('skills_match', {}).get('missing_skills', []))}")

    print("\n" + "="*60)
    print(f"✅ Total candidates screened: {len(results)}")
    print("="*60)

def print_statistics(results):#Print statistics for all the candidates
    """Prints total count of YES, MAYBE and NO recommendations."""
    yes_count = 0
    maybe_count = 0
    no_count = 0
    
    for result in results:
        if result["recommendation"] == "YES":
            yes_count += 1
        elif result["recommendation"] == "MAYBE":
            maybe_count += 1
        else:
            no_count += 1
    
    print(f"Total YES: {yes_count}")
    print(f"Total MAYBE: {maybe_count}")
    print(f"Total NO: {no_count}")


# MAIN PROGRAM
if __name__ == "__main__":

    # ✏️ PASTE YOUR JOB DESCRIPTION HERE
    # Can change accroding to the job requirement
    job_description = """
    Job Title: Data Scientist

    We are looking for a Data Scientist to join our team.

    Requirements:
    - 2+ years of experience in Data Science or Machine Learning
    - Strong Python programming skills
    - Experience with Pandas, NumPy, scikit-learn
    - Knowledge of statistics and data analysis
    - Experience with data visualization (Matplotlib, Seaborn)
    - Familiarity with SQL and databases
    - Strong problem-solving and communication skills

    Nice to have:
    - Experience with Deep Learning (TensorFlow, PyTorch)
    - Knowledge of NLP or Computer Vision
    - Experience with cloud platforms
    - Familiarity with Git and version control
    """

    # 📁 Folder where your PDF resumes are
    resume_folder = "resumes"

    # Create the resumes folder if it doesn't exist
    Path(resume_folder).mkdir(exist_ok=True)

    print("🤖 AI Resume Screening Agent (Powered by Gemini)")
    print("="*50)
    print(f"📁 Looking for resumes in: '{resume_folder}' folder")
    print(f"💼 Screening against: Data Scientist role\n")

    # Run the screening where we run the program
    results = screen_multiple_resumes(resume_folder, job_description)

    if results:
        print_summary(results)#if it gets the results it displays and save them else we it shows add resume to the folder
        print_statistics(results)
        save_report(results)
    else:
        print("\n⚠️  Add PDF resumes to the 'resumes' folder and run again!")#End of the program