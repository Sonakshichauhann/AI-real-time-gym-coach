# 🏋️ AI Real-time Gym Coach

An AI-powered real-time fitness coach that uses **computer vision, pose estimation, exercise-specific form analysis, and AI-generated voice feedback** to help users perform exercises correctly and track their workouts.

The application analyzes the user's body movements through a webcam, counts repetitions, evaluates exercise form, tracks sets, stores workout history, and provides real-time coaching feedback.

---

## 🚀 Features

* 🎥 **Real-time webcam-based exercise detection**
* 🧍 **Human pose estimation using MediaPipe**
* 🔢 **Automatic repetition counting**
* 📊 **Exercise form analysis**
* 🏋️ **Multiple exercise support**
* 🎯 **Set and repetition tracking**
* 🗂️ **Workout history using SQLite**
* 🤖 **AI-powered coaching using Groq LLM**
* 🔊 **Voice feedback using Text-to-Speech**
* 🔐 **User authentication**
* 📈 **Workout progress tracking**
* 💻 **Interactive Streamlit interface**

---

## 🏋️ Supported Exercises

Currently, the coach supports:

| Exercise       | Analysis                                     |
| -------------- | -------------------------------------------- |
| Squats         | Knee position, back posture, squat depth     |
| Push-ups       | Elbow position, body alignment, hip position |
| Biceps Curls   | Elbow position, shoulder movement, swinging  |
| Shoulder Press | Elbow angle, arm extension, back arch        |
| Lunges         | Front knee position, torso posture, balance  |

---

## 🧠 How It Works

```text
                Webcam
                   │
                   ▼
          MediaPipe Pose Detection
                   │
                   ▼
          Body Landmark Extraction
                   │
                   ▼
        Exercise-Specific Detector
                   │
          ┌────────┴────────┐
          ▼                 ▼
    Rep Counting       Form Analysis
          │                 │
          └────────┬────────┘
                   ▼
            Workout Tracking
                   │
          ┌────────┴────────┐
          ▼                 ▼
       SQLite          AI Coach (LLM)
                            │
                            ▼
                    Voice Feedback
```

---

## 🛠️ Tech Stack

### Frontend / Application

* Python
* Streamlit
* Streamlit-WebRTC

### Computer Vision

* OpenCV
* MediaPipe Pose Landmarker
* NumPy

### AI / Generative AI

* Groq API
* LLM-based coaching
* gTTS (Google Text-to-Speech)

### Database

* SQLite

### Other Tools

* Python-dotenv
* Pandas
* Git & GitHub

---

## 📂 Project Structure

```text
AI-Real-Time-Gym-Coach/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── detectors/
│   ├── squat.py
│   ├── pushup.py
│   ├── biceps_curl.py
│   ├── shoulder_press.py
│   └── lunges.py
│
├── services/
│   ├── auth/
│   ├── config/
│   ├── persistence/
│   ├── state/
│   └── ui/
│
├── static/
│
├── ml_models/
│
└── media_pipe_model/
    └── pose_landmarker_full.task
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Real-Time-Gym-Coach.git
cd AI-Real-Time-Gym-Coach
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

The application uses the Groq API for AI-powered coaching.

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

> ⚠️ Never commit your `.env` file or API key to GitHub.

The `.gitignore` file should contain:

```text
.env
```

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run main.py
```

The application will open in your browser.

Allow webcam access when prompted.

---

## 🤖 AI Coach

The application uses a Groq-hosted LLM to generate contextual coaching feedback based on workout events such as:

* Workout started
* Set completed
* Workout completed
* No pose detected
* Exercise form issues
* Ongoing form checks

The AI coach converts workout information into short coaching feedback that can be delivered through voice.

---

## 📊 Workout Tracking

The application tracks information such as:

* Exercise
* Repetitions
* Sets completed
* Target repetitions
* Workout sessions
* Exercise history

Workout information is stored locally using SQLite.

---

## 🔐 Security

API credentials are loaded through environment variables.

Sensitive files such as:

```text
.env
data.db
```

are excluded from version control.

---

## 🎯 Future Improvements

* 📱 Mobile-friendly interface
* 📈 Advanced workout analytics
* 🧠 Personalized workout recommendations
* 🏃 More exercise detectors
* 🔥 Calorie estimation
* 📊 Progress visualization
* 🎙️ More natural conversational voice coaching
* ☁️ Cloud-based workout synchronization
* 👤 Personalized fitness profiles

---

## 🎓 Project Purpose

This project demonstrates the practical application of:

* Computer Vision
* Pose Estimation
* Real-time Video Processing
* AI/LLM Integration
* Voice AI
* Software Engineering
* Database Management
* Streamlit Application Development

It was developed as an **AI/ML project focused on applying computer vision and generative AI to real-world fitness applications.**

---

## 👩‍💻 Author

**Sonakshi Chauhan**

B.Tech Computer Science & Engineering

---

## ⭐ If you like this project

If you find this project interesting, consider giving the repository a ⭐ on GitHub.
