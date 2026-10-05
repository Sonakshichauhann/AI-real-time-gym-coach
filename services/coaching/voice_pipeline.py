import time
import queue
import threading
import collections
import streamlit as st


class VoicePipeline:
    FORM_COOLDOWN = 8  # seconds between spoken form corrections

    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts
        self.last_spoken_at = 0
        self._queue = queue.Queue()
        self._ready = collections.deque()
        self._lock = threading.Lock()
        self._playing_until = 0
        self._issue_key = None      # form issue currently being seen
        self._issue_since = 0       # when it first appeared
        self._squat_min_knee = None # lowest knee angle in the current squat
        threading.Thread(target=self._worker, daemon=True).start()

    def _find_form_issue(self, exercise, metrics):
        if "issue" in metrics:
            return metrics["issue"]

        if exercise == "Squats":
            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)
            
            if depth == "TOO HIGH":
                return "The user's squat is not deep enough — knees are not bending sufficiently."

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "The user is leaning too far forward during the squat."

        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")
            
            if alignment == "Poor Form":
                return "The user's body is not straight during the push-up."

            if hip_status == "SAGGING":
                return "The user's hips are sagging down during the push-up."

            if hip_status == "PIKED UP":
                return "The user's hips are too high — lower them to form a straight line."

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")
            
            if swing == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."

        elif exercise == "Shoulder Press":
            back_arch = metrics.get("back_arch_status", "")
            extension = metrics.get("extension_status", "")
            
            if back_arch == "Excessive Arch":
                return "The user is arching their lower back excessively during the press."

            if back_arch == "Slight Arch":
                return "Slight back arch detected — encourage the user to brace their core."

        elif exercise == "Lunges":
            balance = metrics.get("balance_status", "")
            
            if balance == "OFF BALANCE":
                return "The user is losing balance during the lunge — feet should be hip-width apart."

        return None

    # ------------------------------------------------------------------ text
    CANNED = {
        "workout_started": "Let's begin! Please open your camera and step back so your whole body is visible.",
        "no_pose_detected": "I can't see you. Please step back so your whole body is in the frame.",
        "set_completed": "Great job, set complete! Take a short breather.",
        "workout_completed": "Workout complete! Amazing effort today.",
        "form_issue": "Watch your form and keep your posture correct.",
    }

    def _build_text(self, event, exercise, metrics, detail=None):
        """Return the sentence the coach should say (LLM first, canned fallback)."""
        if event == "workout_started":
            return self.CANNED["workout_started"]      # always tell the user to open the camera

        if event == "rep_completed":
            return f"Rep {detail}" if detail else "Good rep"   # instant, no LLM needed

        issue = self._find_form_issue(exercise, metrics or {})
        try:
            return self.llm.give_feedback(event, issue, detail)
        except Exception as e:
            print(f"[coach] LLM failed ({e}); using built-in sentence")
            if event == "ongoing_form_check":
                return self.CANNED["form_issue"]
            return self.CANNED.get(event, self.CANNED["form_issue"])

    def _speak(self, text):
        try:
            return self.tts.speak(text)
        except Exception as e:
            print(f"[coach] text-to-speech failed: {e}")
            return None

    # --------------------------------------------------- synchronous (buttons)
    def process_event(self, event, exercise, metrics, detail=None):
        issue = self._find_form_issue(exercise, metrics or {})
        now = time.time()
        is_major = event in ["workout_started", "set_completed", "workout_completed", "rep_completed"]

        if not is_major:
            if not issue or now - self.last_spoken_at < self.FORM_COOLDOWN:
                return None

        text = self._build_text(event, exercise, metrics, detail)
        voice = self._speak(text)
        self.last_spoken_at = now
        return voice, text

    # ------------------------------------------- background (live workout loop)
    def _worker(self):
        while True:
            event, exercise, metrics, detail, created = self._queue.get()
            text = self._build_text(event, exercise, metrics, detail)
            audio = self._speak(text)
            with self._lock:
                self._ready.append((audio, text, event, created))

    def submit(self, event, exercise, metrics, detail=None):
        """Queue an event for the background worker. Never blocks the UI loop.
        Returns True if it was queued."""
        now = time.time()
        major = event in ["set_completed", "workout_completed", "rep_completed", "workout_started"]

        if not major:  # form corrections / no-pose
            metrics = dict(metrics or {})

            # Squat depth: judge the whole rep (lowest point reached before standing up)
            if event == "ongoing_form_check" and exercise == "Squats":
                knee = metrics.get("knee_angle") or 0
                if 0 < knee < 150:
                    self._squat_min_knee = knee if self._squat_min_knee is None else min(self._squat_min_knee, knee)
                elif knee >= 150 and self._squat_min_knee is not None:
                    if self._squat_min_knee > 105:
                        metrics["issue"] = "The user's squat is not deep enough — go lower until thighs are near parallel."
                    self._squat_min_knee = None

            issue = metrics.get("issue") or self._find_form_issue(exercise, metrics)

            if not issue:
                self._issue_key = None
                return False

            # require the problem to persist ~1 second so brief glitches don't trigger speech
            if issue != self._issue_key:
                self._issue_key = issue
                self._issue_since = now
            instant = event == "no_pose_detected" or "not deep enough" in issue
            if not instant and now - self._issue_since < 1.0:
                return False

            if now - self.last_spoken_at < self.FORM_COOLDOWN or self._queue.qsize() > 0:
                return False
            self.last_spoken_at = now
            metrics["issue"] = issue

        self._queue.put((event, exercise, dict(metrics or {}), detail, now))
        return True

    def pop_result(self):
        """Return the next (audio, text) that is safe to play, or None.
        Waits until the previous clip has finished so audio never overlaps."""
        now = time.time()
        with self._lock:
            if now < self._playing_until or not self._ready:
                return None
            audio, text, event, created = self._ready.popleft()
            # drop stale form tips (user has probably already corrected themselves)
            while event in ("ongoing_form_check", "no_pose_detected") and now - created > 8 and self._ready:
                audio, text, event, created = self._ready.popleft()

        if audio:
            self._playing_until = now + len(audio) / 4000 + 0.5   # rough mp3 length
        return audio, text


def autoplay_audio(audio_bytes):
    if not audio_bytes:
        return
    
    st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
    
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)