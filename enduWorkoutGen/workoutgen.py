from dataclasses import dataclass
from enum import Enum
import random
from typing import List, Tuple
import os
from datetime import datetime

class WorkoutType(Enum):
    ENDURANCE = "endurance"
    THRESHOLD = "threshold"
    VO2 = "vo2"
    TEMPO = "tempo"
    Z2 = "z2"
    SPRINTS = "sprints"

    @classmethod
    def list_workout_types(cls):
        print("\nAvailable Workout Types and their characteristics:")
        workout_info = {
            "ENDURANCE": "Long, steady efforts at 65-75% FTP. Good for building base fitness.",
            "THRESHOLD": "Work at or near FTP (95-105%). Improves sustainable power.",
            "VO2": "High intensity intervals (106-120% FTP). Improves maximum oxygen uptake.",
            "TEMPO": "Moderately hard efforts (85-95% FTP). Builds aerobic capacity.",
            "Z2": "Easy to moderate intensity (56-75% FTP). Recovery and base building.",
            "SPRINTS": "Very high intensity efforts (130-200% FTP) with recovery periods."
        }
        for workout_type, description in workout_info.items():
            print(f"\n{workout_type}:")
            print(f"    {description}")
@dataclass
class WorkoutParameters:
    workout_type: WorkoutType
    duration_minutes: int
    ftp: int


@dataclass
class WorkoutInterval:
    start_time: int  # seconds
    end_time: int  # seconds
    power: int  # watts


class WorkoutGenerator:
    def __init__(self):
        # Define intensity ranges for each workout type as percentage of FTP
        self.intensity_ranges = {
            WorkoutType.ENDURANCE: (65, 75),
            WorkoutType.THRESHOLD: (95, 105),
            WorkoutType.VO2: (106, 120),
            WorkoutType.TEMPO: (85, 95),
            WorkoutType.Z2: (56, 75),
            WorkoutType.SPRINTS: (130, 200)
        }

        # Define typical interval durations for each type (in seconds)
        self.interval_durations = {
            WorkoutType.ENDURANCE: (600, 1800),
            WorkoutType.THRESHOLD: (180, 600),
            WorkoutType.VO2: (30, 300),
            WorkoutType.TEMPO: (300, 1200),
            WorkoutType.Z2: (600, 1800),
            WorkoutType.SPRINTS: (15, 30)
        }
        # Add workout descriptions and naming patterns
        self.workout_names = {
            WorkoutType.ENDURANCE: [
                "Long and Steady", "Base Builder", "Endurance Foundation",
                "Distance Driver", "Aerobic Builder"
            ],
            WorkoutType.THRESHOLD: [
                "FTP Booster", "Threshold Builder", "Sweet Spot Special",
                "Power Hour", "Threshold Challenge"
            ],
            WorkoutType.VO2: [
                "Oxygen Hunter", "VO2 Crusher", "Peak Power",
                "Red Zone", "Lung Buster"
            ],
            WorkoutType.TEMPO: [
                "Tempo Time", "Sustained Power", "Rhythm Rider",
                "Tempo Builder", "Steady State"
            ],
            WorkoutType.Z2: [
                "Easy Rider", "Recovery Spin", "Active Rest",
                "Zone 2 Foundation", "Base Miles"
            ],
            WorkoutType.SPRINTS: [
                "Sprint King", "Power Burst", "Lightning Rounds",
                "Quick Strike", "Speed Demon"
            ]
        }

    def generate_workout_name(self, workout_type: WorkoutType, duration_minutes: int) -> str:
        """Generate a meaningful workout name"""
        base_name = random.choice(self.workout_names[workout_type])
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{timestamp}_{base_name}_{duration_minutes}min"

    def create_workout_description(self, params: WorkoutParameters) -> str:
        """Create a meaningful workout description"""
        intensity_range = self.intensity_ranges[params.workout_type]
        base_descriptions = {
            WorkoutType.ENDURANCE: f"Endurance workout targeting {intensity_range[0]}-{intensity_range[1]}% of FTP. Focus on maintaining steady power.",
            WorkoutType.THRESHOLD: f"Threshold intervals at {intensity_range[0]}-{intensity_range[1]}% of FTP. Building sustainable power.",
            WorkoutType.VO2: f"VO2max intervals at {intensity_range[0]}-{intensity_range[1]}% of FTP. High-intensity work to improve oxygen uptake.",
            WorkoutType.TEMPO: f"Tempo work at {intensity_range[0]}-{intensity_range[1]}% of FTP. Sustained moderate-intensity efforts.",
            WorkoutType.Z2: f"Zone 2 training at {intensity_range[0]}-{intensity_range[1]}% of FTP. Building aerobic base.",
            WorkoutType.SPRINTS: f"Sprint intervals up to {intensity_range[1]}% of FTP with recovery periods. Improving peak power."
        }

        return (f"{base_descriptions[params.workout_type]}\n"
                f"Duration: {params.duration_minutes} minutes\n"
                f"Target FTP: {params.ftp} watts")

    def create_filename(self, workout_name: str, file_type: str = "mrc") -> str:
        """Create a properly formatted filename"""
        # Replace spaces with underscores and remove special characters
        clean_name = "".join(c if c.isalnum() or c in "._- " else "" for c in workout_name)
        clean_name = clean_name.replace(" ", "_")
        return f"{clean_name}.{file_type}"

    def generate_workout(self, params: WorkoutParameters) -> List[WorkoutInterval]:
        intervals = []
        current_time = 0
        duration_seconds = params.duration_minutes * 60

        # Always start with a 5-minute warmup
        warmup_duration = 300
        intervals.append(WorkoutInterval(0, warmup_duration, int(params.ftp * 0.5)))
        current_time = warmup_duration

        # Generate main intervals
        while current_time < (duration_seconds - 300):  # Leave room for cooldown
            if params.workout_type == WorkoutType.SPRINTS:
                # Special handling for sprints: include recovery
                sprint_duration = random.randint(15, 30)
                recovery_duration = random.randint(60, 180)

                sprint_power = int(params.ftp * random.uniform(
                    self.intensity_ranges[params.workout_type][0] / 100,
                    self.intensity_ranges[params.workout_type][1] / 100
                ))

                intervals.append(WorkoutInterval(
                    current_time,
                    current_time + sprint_duration,
                    sprint_power
                ))

                intervals.append(WorkoutInterval(
                    current_time + sprint_duration,
                    current_time + sprint_duration + recovery_duration,
                    int(params.ftp * 0.5)
                ))

                current_time += sprint_duration + recovery_duration
            else:
                # Regular interval generation
                interval_duration = random.randint(
                    *self.interval_durations[params.workout_type]
                )

                if current_time + interval_duration > duration_seconds - 300:
                    interval_duration = duration_seconds - 300 - current_time

                power = int(params.ftp * random.uniform(
                    self.intensity_ranges[params.workout_type][0] / 100,
                    self.intensity_ranges[params.workout_type][1] / 100
                ))

                intervals.append(WorkoutInterval(
                    current_time,
                    current_time + interval_duration,
                    power
                ))

                current_time += interval_duration

        # Add cooldown
        intervals.append(WorkoutInterval(
            current_time,
            duration_seconds,
            int(params.ftp * 0.5)
        ))

        return intervals

    def calculate_metrics(self, intervals: List[WorkoutInterval], ftp: int) -> Tuple[float, int]:
        """Calculate TSS and estimated kcal for the workout"""
        total_tss = 0
        total_kj = 0

        for interval in intervals:
            duration_hours = (interval.end_time - interval.start_time) / 3600
            intensity_factor = interval.power / ftp
            tss = 100 * duration_hours * intensity_factor ** 2

            # Calculate work in kilojoules (power * time in seconds)
            work = interval.power * (interval.end_time - interval.start_time)
            total_kj += work

            total_tss += tss

        # Estimate kcal (roughly 4.18 kilojoules per kcal)
        estimated_kcal = int(total_kj / 4.18)

        return round(total_tss, 1), estimated_kcal

    def export_mrc(self, intervals: List[WorkoutInterval], filename: str, description: str):
        """Export workout to MRC format with enhanced description"""
        with open(filename, 'w') as f:
            f.write("[COURSE HEADER]\n")
            f.write("VERSION = 2\n")
            f.write("UNITS = ENGLISH\n")
            f.write(f"DESCRIPTION = {description}\n")
            f.write(f"FILE NAME = {os.path.basename(filename)}\n")
            f.write("[END COURSE HEADER]\n\n")

            f.write("[COURSE DATA]\n")
            for interval in intervals:
                f.write(f"{interval.start_time}\t{interval.power}\n")
                f.write(f"{interval.end_time}\t{interval.power}\n")
            f.write("[END COURSE DATA]\n")

