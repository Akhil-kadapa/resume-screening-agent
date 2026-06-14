# 🤖 AI Resume Screening Agent

An intelligent resume screening tool 
built with Python and Google Gemini AI 
that automatically evaluates, scores, 
and ranks candidates against a job description.

## 📋 What It Does
- Reads multiple PDF resumes automatically
- Uses Gemini AI to analyze each resume
- Scores candidates on skills, experience 
  and education
- Ranks candidates from best to least fit
- Saves results to CSV report

## 🛠️ Tech Stack
- Python 3.x
- Google Gemini API (gemini-2.5-flash)
- PyPDF2
- JSON / CSV

## ⚙️ Setup Instructions

### 1. Install dependencies
pip install google-generativeai pypdf2

### 2. Add your API key
Get free key from: aistudio.google.com
Open agent.py and replace:
API_KEY = "your-api-key-here"

### 3. Add PDF resumes
Create a resumes/ folder and 
add PDF resumes inside it

### 4. Run
python agent.py

## 📊 Sample Output
🟢 Rank 1: John Smith - 98/100 YES
🟡 Rank 2: Akhil Kadapa - 67/100 MAYBE  
🔴 Rank 3: Sarah Jones - 29/100 NO

Total YES: 1
Total MAYBE: 1
Total NO: 1

## 🧠 What I Learned Building This
- Python functions and function chaining
- Google Gemini API integration
- Prompt engineering for structured output
- PDF processing with PyPDF2
- JSON data handling
- Error debugging and handling
- Lambda functions and sorting
- String slicing and manipulation
- File handling with pathlib

## 👨‍💻 Author
Ahamed Akhil Kadapa
M.S. Artificial Intelligence
University of Bridgeport
GitHub: github.com/Akhil-Kadapa