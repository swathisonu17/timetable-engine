


import os
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import random

st.set_page_config(page_title="Department Timetable Engine", layout="wide")

# ===============================
# DATA SETUP & PERSISTENCE
# ===============================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(name, cols):
    path = f"{DATA_DIR}/{name}.csv"
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=cols)

def save_csv(df, name):
    df.to_csv(f"{DATA_DIR}/{name}.csv", index=False)

faculty_df  = load_csv("faculty",  ["Faculty"])
subject_df  = load_csv("subject",  ["Subject"])
section_df  = load_csv("section",  ["Section"])
semester_df = load_csv("semester", ["Semester"])
mapping_df  = load_csv("mapping",  ["Faculty","Subject","Section","Semester","Type","Batch"])

# ===============================
# UI SIDEBAR
# ===============================
st.sidebar.title("🗂 Timetable Engine")
menu = st.sidebar.radio("Menu", ["Dashboard","Enter Data","Generate Timetable"])

if menu == "Dashboard":
    st.title("📊 Dashboard")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Faculty", len(faculty_df))
    c2.metric("Subjects", len(subject_df))
    c3.metric("Sections", len(section_df))
    c4.metric("Mappings", len(mapping_df))

elif menu == "Enter Data":
    st.title("📝 Data Entry")
    # ... (Your existing Form logic for Faculty, Subject, Section, Semester, and Mapping)
    # [KEEP YOUR EXISTING FORM CODE HERE]
    with st.form("mapping"):
        f = st.selectbox("Faculty", faculty_df["Faculty"]) if not faculty_df.empty else None
        s = st.selectbox("Subject", subject_df["Subject"]) if not subject_df.empty else None
        sec = st.selectbox("Section", section_df["Section"]) if not section_df.empty else None
        sem = st.selectbox("Semester", semester_df["Semester"]) if not semester_df.empty else None
        t = st.radio("Type", ["Theory","Lab"])
        b = st.selectbox("Batch", ["-","B-1","B-2"])
        if st.form_submit_button("Add Mapping"):
            mapping_df.loc[len(mapping_df)] = [f,s,sec,sem,t,b]
            save_csv(mapping_df,"mapping")
            st.success("Mapping Added!")
    st.dataframe(mapping_df)

# ===============================
# THE GENERATION ENGINE (Refined & Complete)
# ===============================

elif menu == "Generate Timetable":

    st.title("📅 Final Timetable: Complete Lab Coverage")
    random.seed(42)  # Comment this out with # to stop locking

    if mapping_df.empty:
        st.warning("⚠ Please add subject mappings first!")
        st.stop()

    available_sems = sorted(mapping_df["Semester"].unique())
    selected_sem = st.selectbox("Select Semester", available_sems)
    
    days = ["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"]
    time_columns = ["09:00-10:00", "10:00-11:00", "11:00-11:15 BREAK", "11:15-12:15", "12:15-01:15", "01:15-02:00 LUNCH", "02:00-03:00", "03:00-04:00"]
    teaching_slots = ["09:00-10:00", "10:00-11:00", "11:15-12:15", "12:15-01:15", "02:00-03:00", "03:00-04:00"]
    lab_blocks = [("09:00-10:00", "10:00-11:00"), ("11:15-12:15", "12:15-01:15"), ("02:00-03:00", "03:00-04:00")]
    
    if 'global_faculty_busy' not in st.session_state:
        st.session_state.global_faculty_busy = set() 

    def style_timetable(val):
        if "\n/\n" in str(val):
           return 'color: #D5F5E3; font-weight: 700; white-space: pre-wrap; text-align: center;'
        if any(x in str(val) for x in ["B\nR\nE\nA\nK", "L\nU\nN\nC\nH"]):
            return 'font-weight: bold; text-align: center; white-space: pre-wrap;'
        return 'text-align: center;'

    sections = sorted(mapping_df[mapping_df["Semester"] == selected_sem]["Section"].unique())
    
    for section in sections:
        st.subheader(f"📍 Timetable: {section}")
        tt = pd.DataFrame("", index=days, columns=time_columns)
        
        # 2. Place labels only once in the middle of the week
        # This prevents the text from repeating every single day

        tt.at["WEDNESDAY", "11:00-11:15 BREAK"] = "B\nR\nE\nA\nK"
        tt.at["WEDNESDAY", "01:15-02:00 LUNCH"] = "L\nU\nN\nC\nH"
        

        sec_data = mapping_df[(mapping_df["Semester"] == selected_sem) & (mapping_df["Section"] == section)]

        # --- THE ULTIMATE 5-DAY LAB ROTATION ---
        lab_entries = sec_data[sec_data["Type"] == "Lab"].to_dict('records')
        u_labs = {l['Subject']: l for l in lab_entries}
        
        # Extract specific labs based on your requirements
        # Note: We use .get() to avoid errors if a subject is named slightly differently
        names = list(u_labs.keys())
        # We'll map them dynamically but ensure the 5 pairs match your logic
        # 1. JAVA(B1)/DDCO(B2) | 2. DDCO(B1)/JAVA(B2) | 3. OS(B1)/DSA(B2) | 4. EXCEL(B1)/OS(B2) | 5. DSA(B1)/EXCEL(B2)
        
        # Sorting to ensure consistent assignment across runs
        names.sort() 
        if len(names) >= 5:
            # Manually building the rotation to match your requested pairings
            # Adjust these indices if your naming order is different
            j, ddc, o, ds, ex = names[0], names[1], names[2], names[3], names[4]
            rotations = [
                (j, ddc), # JAVA(B1) / DDCO(B2)
                (ddc, j), # DDCO(B1) / JAVA(B2)
                (o, ds),  # OS(B1)   / DSA(B2)
                (ex, o),  # EXCEL(B1)/ OS(B2)
                (ds, ex)  # DSA(B1)  / EXCEL(B2) <-- NEW: Completes the set
            ]
        else:
            rotations = []

        assigned_lab_days = set()
        for sub_a, sub_b in rotations:
            placed = False
            for d in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                if d in assigned_lab_days: continue
                random.shuffle(lab_blocks)
                for s1, s2 in lab_blocks:
                    f1, f2 = u_labs[sub_a]['Faculty'], u_labs[sub_b]['Faculty']
                    if f1 != f2: # Strict teacher check
                        if not any(x in st.session_state.global_faculty_busy for x in [(f1, d, s1), (f1, d, s2), (f2, d, s1), (f2, d, s2)]):
                            tt.at[d, s1] = tt.at[d, s2] = f"{sub_a} LAB(B1)\n/\n{sub_b} LAB(B2)"
                            st.session_state.global_faculty_busy.update([(f1, d, s1), (f1, d, s2), (f2, d, s1), (f2, d, s2)])
                            assigned_lab_days.add(d); placed = True; break
                if placed: break        

        # --- THEORY FILLING ---
        theory_subjects = sec_data[sec_data["Type"] == "Theory"].to_dict('records')
        for theory in theory_subjects:
            needed = 3
            for d in days:
                if needed <= 0: break
                random.shuffle(teaching_slots)
                for s in teaching_slots:
                    if tt.at[d, s] == "" and (theory['Faculty'], d, s) not in st.session_state.global_faculty_busy:
                        if not any(theory['Subject'] in str(cell) for cell in tt.loc[d]):
                            tt.at[d, s] = f"{theory['Subject']}\n({theory['Faculty']})"
                            st.session_state.global_faculty_busy.add((theory['Faculty'], d, s))
                            needed -= 1; break

        st.dataframe(tt.style.applymap(style_timetable), use_container_width=True)
  

    # # Workload Summary
    st.header("📊 Faculty Workload Summary")
    workload_data = []

    # Ensure the name here (f) matches the name inside the sum function
    for f in faculty_df["Faculty"]:
        total_slots = sum(1 for item in st.session_state.global_faculty_busy if item[0] == f)
        workload_data.append({"Faculty": f, "Total Weekly Slots": total_slots})
    st.table(pd.DataFrame(workload_data).sort_values("Total Weekly Slots", ascending=False))    
    
