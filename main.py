from enduWorkoutGen.workoutgen import WorkoutGenerator, WorkoutParameters, WorkoutType, WorkoutSegment

# Print available workout types
WorkoutType.list_workout_types()



# Example usage:
generator = WorkoutGenerator()
workout_params = WorkoutParameters(
    segments=[
        WorkoutSegment(WorkoutType.TEMPO, 20),
        WorkoutSegment(WorkoutType.VO2, 15),
        WorkoutSegment(WorkoutType.THRESHOLD, 25)
    ],
    total_duration_minutes=60
)

intervals = generator.generate_workout(workout_params)
workout_name = generator.generate_workout_name(workout_params)
description = generator.create_workout_description(workout_params)
filename = generator.create_filename(workout_name)
generator.export_mrc(intervals, filename, description)


# Calculate metrics
tss = generator.calculate_metrics(intervals)

# Create filename
filename = generator.create_filename(workout_name)

# Print workout details
print(f"\nWorkout Details:")
print(f"Name: {workout_name}")
print(f"\nDescription:")
print(description)
print(f"\nMetrics:")
print(f"TSS: {tss}")
print(f"\nFile saved as: {filename}")

# Export to MRC file
generator.export_mrc(intervals, filename, description)

# Export to ZWO file
generator.export_zwo(intervals, filename, description)