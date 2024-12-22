from enduWorkoutGen.workoutgen import WorkoutGenerator, WorkoutParameters, WorkoutType

# Print available workout types
WorkoutType.list_workout_types()

# Example usage
generator = WorkoutGenerator()

# Create workout parameters
params = WorkoutParameters(
    workout_type=WorkoutType.THRESHOLD,
    duration_minutes=60,
)

# Generate workout name and description
workout_name = generator.generate_workout_name(params.workout_type, params.duration_minutes)
workout_description = generator.create_workout_description(params)

# Generate the workout
intervals = generator.generate_workout(params)

# Calculate metrics
tss = generator.calculate_metrics(intervals)

# Create filename
filename = generator.create_filename(workout_name)

# Print workout details
print(f"\nWorkout Details:")
print(f"Name: {workout_name}")
print(f"\nDescription:")
print(workout_description)
print(f"\nMetrics:")
print(f"TSS: {tss}")
print(f"\nFile saved as: {filename}")

# Export to MRC file
generator.export_mrc(intervals, filename, workout_description)