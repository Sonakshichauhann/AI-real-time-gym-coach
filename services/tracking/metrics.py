import streamlit as st
import time
from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise


def sync_metrics_update(context):
    if not context or not hasattr(context, "state") or not context.state.playing:
        return
    
    processor = getattr(context, "video_processor", None)

    if not processor:
        return 
    
    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return
    
    processor.set_exercise(exercise)
    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return
    
    reps = latest_metrics.get("reps", 0)

    if reps is None:
        reps = 0
        
    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return 

    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    reps_per_set = st.session_state.get("reps_per_set", 0)
    target_sets = st.session_state.get("target_sets", 0)

    if reps is not None and reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_set_reps = reps % reps_per_set
        workout_completed = sets_completed >= target_sets 
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed

    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)
    pipeline = st.session_state.get("voice_pipeline")

    set_just_completed = target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets
    workout_just_completed = workout_completed and not st.session_state.get("last_notified_workout_complete", False)

    # ---- save finished sets to the database ----
    if set_just_completed:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = now_ts - started_at
        user_id = st.session_state.get("user_id", 0)

        add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)

        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed

    # ---- voice announcements (non-blocking) ----
    if workout_just_completed:
        st.session_state.last_notified_workout_complete = True
        if pipeline:
            pipeline.submit("workout_completed", exercise, latest_metrics,
                            detail=f"Finished all {target_sets} sets of {reps_per_set} reps")
    elif set_just_completed:
        if pipeline:
            pipeline.submit("set_completed", exercise, latest_metrics,
                            detail=f"Completed set {sets_completed} of {target_sets}")

    # ---- form corrections / no pose ----
    if pipeline:
        if not latest_metrics.get("pose_detected", True):
            pipeline.submit("no_pose_detected", exercise,
                            {"issue": "No pose detected! Please step into the camera frame."})
        else:
            pipeline.submit("ongoing_form_check", exercise, latest_metrics)