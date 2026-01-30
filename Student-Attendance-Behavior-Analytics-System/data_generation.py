import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# ------------------ Step 1: Setup ------------------
np.random.seed(42)
days = 200
end_date = datetime.now()
start_date = end_date - timedelta(days=280)
academic_dates = pd.date_range(start=start_date, end=end_date, freq="B")  # Weekdays only

# ------------------ Step 2: Fixed Subject Schedule ------------------
subjects = ["maths", "science", "english", "computer", "economics"]
subject_schedule = {
    "maths": [0, 2, 4], "science": [1, 3],
    "english": [0, 3], "computer": [1, 4], "economics": [2]
}
schedule_rows = [{"subject": sub, "weekday": wd} for sub, wds in subject_schedule.items() for wd in wds]
schedule_df = pd.DataFrame(schedule_rows)

# ------------------ Step 3: Student Profiles ------------------
num_students = 300
student_ids = np.arange(1, num_students + 1)
behavior_types_list = ["disciplined", "borderline", "chronic"]
behavior_types = np.random.choice(behavior_types_list, size=num_students, p=[0.65,0.25,0.10])

# ------------------ Step 4: Attendance Probability ------------------
subject_difficulty = {"maths":0.9, "science":0.85, "english":0.95, "computer":0.9, "economics":0.9}
base_prob = {"disciplined":0.95, "borderline":0.75, "chronic":0.5}
mid_term_day_index = len(academic_dates) // 2
mid_term_effect = {"disciplined":0.0, "borderline":0.05, "chronic":0.10}
mass_bunk_dates = [academic_dates[50], academic_dates[51]]
mass_bunk_factor = 0.5

def compute_final_prob(student_type, subject, current_date):
    prob = base_prob[student_type] * subject_difficulty[subject]
    if current_date >= academic_dates[mid_term_day_index]:
        months_after = ((current_date - academic_dates[mid_term_day_index]).days) // 30
        prob -= months_after * mid_term_effect[student_type]
        prob = max(prob,0)
    if current_date in mass_bunk_dates:
        prob *= mass_bunk_factor
    return np.clip(prob,0,1)

# ------------------ Step 5: Session Expansion ------------------
attendance_rows = []
for current_date in academic_dates:
    weekday = current_date.weekday()
    todays_subjects = schedule_df[schedule_df['weekday']==weekday]['subject'].tolist()
    for subject in todays_subjects:
        for idx, student_id in enumerate(student_ids):
            student_type = behavior_types[idx]
            prob = compute_final_prob(student_type, subject, current_date)
            attendance = 1 if np.random.rand() < prob else 0
            attendance_rows.append({
                "date": current_date,
                "weekday": weekday,
                "student_id": student_id,
                "behavior_type": student_type,
                "subject": subject,
                "attendance": attendance
            })
attendance_df = pd.DataFrame(attendance_rows)
attendance_df['month'] = attendance_df['date'].dt.month
attendance_df['week'] = attendance_df['date'].dt.isocalendar().week

# Save main dataset
attendance_df.to_csv("attendance.csv", index=False)

# ------------------ Step 6: Analysis ------------------
attendance_df['mean_attendance'] = attendance_df.groupby('student_id')['attendance'].transform('mean')
low_attendance_students = attendance_df[attendance_df['mean_attendance'] < 0.75]
problematic_subject = attendance_df.groupby('subject')['attendance'].mean().sort_values()
overall_monthly_trends = attendance_df.groupby(['month','behavior_type'])['attendance'].mean().unstack()
subject_wise_monthly_trends = attendance_df.groupby(['month','subject'])['attendance'].mean().unstack()
perfect_attendance_ids = attendance_df.groupby('student_id')['attendance'].mean().pipe(lambda x: x[x==1].index.tolist())
chronic_absentee_ids = attendance_df.groupby('student_id')['attendance'].mean().pipe(lambda x: x[x<0.5].index.tolist())
weekday_subject_pattern = attendance_df.groupby(['weekday','subject'])['attendance'].mean().unstack()

# ------------------ Step 6a: Top-N reports ------------------
TOP_N = 10
top_low_attendance_students = low_attendance_students.groupby('student_id')['attendance'].mean().sort_values().head(TOP_N)
worst_subjects = problematic_subject.head(TOP_N)

# Save analysis CSVs
low_attendance_students.to_csv("low_attendance_students.csv", index=False)
attendance_df.groupby('subject')['attendance'].mean().sort_values().to_csv("subject_attendance_summary.csv")
overall_monthly_trends.to_csv("overall_monthly_trends.csv")
subject_wise_monthly_trends.to_csv("subject_wise_monthly_trends.csv")
pd.DataFrame({"perfect_attendance_ids": perfect_attendance_ids}).to_csv("perfect_attendance_students.csv", index=False)
pd.DataFrame({"chronic_absentee_ids": chronic_absentee_ids}).to_csv("chronic_absentee_students.csv", index=False)

# ------------------ Step 8: Dashboard ------------------
dashboard = pd.DataFrame({"student_id": student_ids})
dashboard['behavior_type'] = [behavior_types[idx] for idx in range(len(student_ids))]
dashboard['mean_attendance'] = dashboard['student_id'].map(attendance_df.groupby('student_id')['attendance'].mean())
dashboard['perfect_attendance'] = dashboard['student_id'].isin(perfect_attendance_ids)
dashboard['chronic_absentee'] = dashboard['student_id'].isin(chronic_absentee_ids)
dashboard['attendance_rank'] = dashboard['mean_attendance'].rank(method='min', ascending=True)
dashboard.to_csv("attendance_summary_dashboard.csv", index=False)

# ------------------ Step 9 & 10: Visualization -> PDF ------------------
sns.set_style("whitegrid")
pdf_path = "attendance_report.pdf"
with PdfPages(pdf_path) as pdf:
    # Problematic subjects
    plt.figure(figsize=(8,5))
    sns.barplot(x=problematic_subject.index, y=problematic_subject.values, palette="magma")
    plt.title("Average Attendance per Subject")
    plt.ylabel("Average Attendance")
    plt.xlabel("Subject")
    plt.ylim(0,1)
    pdf.savefig()
    plt.close()

    # Monthly trends by behavior type
    plt.figure(figsize=(10,6))
    overall_monthly_trends.plot(kind='line', marker='o')
    plt.title("Monthly Attendance Trends by Behavior Type")
    plt.ylabel("Average Attendance")
    plt.xlabel("Month")
    plt.ylim(0,1)
    plt.grid(True)
    pdf.savefig()
    plt.close()

    # Subject-wise monthly trends heatmap
    plt.figure(figsize=(10,6))
    sns.heatmap(subject_wise_monthly_trends.T, annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title("Subject-wise Monthly Attendance")
    plt.xlabel("Month")
    plt.ylabel("Subject")
    pdf.savefig()
    plt.close()

    # Weekday-subject pattern heatmap
    plt.figure(figsize=(10,5))
    sns.heatmap(weekday_subject_pattern.T, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Weekday-Subject Attendance Pattern")
    plt.xlabel("Weekday (0=Mon)")
    plt.ylabel("Subject")
    pdf.savefig()
    plt.close()

    # Top-N low-attendance students
    plt.figure(figsize=(10,6))
    sns.barplot(x=top_low_attendance_students.index, y=top_low_attendance_students.values, palette="Reds_r")
    plt.title(f"Top-{TOP_N} Low-Attendance Students")
    plt.xlabel("Student ID")
    plt.ylabel("Average Attendance")
    plt.ylim(0,1)
    pdf.savefig()
    plt.close()

    # Worst subjects
    plt.figure(figsize=(8,5))
    sns.barplot(x=worst_subjects.index, y=worst_subjects.values, palette="Oranges_r")
    plt.title(f"Top-{TOP_N} Worst Subjects by Attendance")
    plt.ylabel("Average Attendance")
    plt.xlabel("Subject")
    plt.ylim(0,1)
    pdf.savefig()
    plt.close()

print(f"✅ PDF report saved as '{pdf_path}'")
print("✅ All CSVs saved in the folder")