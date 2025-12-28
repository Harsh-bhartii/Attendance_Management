import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import sys

def run_attendance(interactive=True, demo=False, no_plot=False):
	if demo:
		# create sample/demo data
		num_students = 3
		num_days = 5
		students = ["Alice", "Bob", "Charlie"]
		dates = pd.date_range(end=pd.Timestamp.today(), periods=num_days).strftime("%d-%m-%Y").tolist()
		attendance_data = []
		for date in dates:
			for student in students:
				# 80% chance present
				status = "Present" if np.random.rand() < 0.8 else "Absent"
				attendance_data.append([date, student, status])
	else:
		try:
			num_students = int(input("Enter number of students: "))
			num_days = int(input("Enter number of days: "))
		except (EOFError, KeyboardInterrupt):
			print("\nNo interactive input available. Run with --demo or provide input interactively.")
			sys.exit(1)

		students = []
		for i in range(num_students):
			name = input(f"Enter name of student {i+1}: ")
			students.append(name)

		attendance_data = []
		for day in range(num_days):
			date = input(f"\nEnter date for Day {day+1} (DD-MM-YYYY): ")
			for student in students:
				status = input(f"Is {student} Present or Absent on {date}? ").strip().capitalize()
				while status not in ["Present", "Absent"]:
					print("Invalid input! Please enter Present or Absent.")
					status = input(f"Is {student} Present or Absent on {date}? ").strip().capitalize()
				attendance_data.append([date, student, status])

	# create dataframe and process (same logic as before)
	df = pd.DataFrame(attendance_data, columns=["Date", "Name", "Status"])
	df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors='coerce')
	# drop invalid dates if any
	if df["Date"].isna().any():
		print("Warning: Some dates couldn't be parsed and will be dropped.")
		df = df.dropna(subset=["Date"])

	out_csv = "attendance.csv"
	df.to_csv(out_csv, index=False)
	print(f"\nAttendance data saved to {out_csv}")

	df["Attendance"] = np.where(df["Status"].str.lower() == "present", 1, 0)
	total_present = int(np.sum(df["Attendance"]))
	total_absent = int(len(df) - total_present)

	attendance_percentage = df.groupby("Name")["Attendance"].mean() * 100

	report = df.groupby("Name").agg(
		Total_Days=("Attendance", "count"),
		Days_Present=("Attendance", "sum")
	)
	report["Attendance_%"] = (report["Days_Present"] / report["Total_Days"]) * 100

	print("\nTotal Present:", total_present)
	print("Total Absent:", total_absent)
	print("\nAttendance Percentage:")
	print(attendance_percentage)
	print("\nDetailed Attendance Report:")
	print(report)

	# plotting: either show or save depending on no_plot
	if no_plot:
		plt.switch_backend("Agg")
	attendance_percentage.plot(kind="bar")
	plt.title("Attendance Percentage per Student")
	plt.ylabel("Percentage")
	plt.ylim(0, 100)
	plt.grid(axis="y")
	if no_plot:
		plt.savefig("attendance_percentage.png", bbox_inches="tight")
		print("Saved plot to attendance_percentage.png")
	else:
		plt.show()
	plt.clf()

	daily_attendance = df.groupby("Date")["Attendance"].sum()
	plt.plot(daily_attendance.index, daily_attendance.values, marker="o")
	plt.title("Daily Attendance Trend")
	plt.xlabel("Date")
	plt.ylabel("Number of Students Present")
	plt.grid()
	if no_plot:
		plt.savefig("daily_attendance_trend.png", bbox_inches="tight")
		print("Saved plot to daily_attendance_trend.png")
	else:
		plt.show()

def main():
	parser = argparse.ArgumentParser(description="Attendance management")
	parser.add_argument("--demo", action="store_true", help="Run with demo/sample data (non-interactive)")
	parser.add_argument("--no-plot", action="store_true", help="Don't show plots (save to files instead)")
	args = parser.parse_args()

	# If no DISPLAY and not explicitly allowing plots, force no-plot to avoid errors in headless envs
	if not args.no_plot and not os.environ.get("DISPLAY"):
		args.no_plot = True

	if args.demo:
		run_attendance(interactive=False, demo=True, no_plot=args.no_plot)
	else:
		run_attendance(interactive=True, demo=False, no_plot=args.no_plot)

if __name__ == "__main__":
	main()



