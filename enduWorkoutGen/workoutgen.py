import xml.etree.ElementTree as ET
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


@dataclass
class WorkoutInterval:
    start_time: int  # seconds
    end_time: int  # seconds
    power: int  # watts
@dataclass
class WorkoutSegment:
    workout_type: WorkoutType
    duration_minutes: int
@dataclass
class WorkoutParameters:
    segments: List[WorkoutSegment]
    total_duration_minutes: int


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

    def generate_workout_name(self, params: WorkoutParameters) -> str:
        """Generate a meaningful workout name for mixed workout"""
        workout_types = [segment.workout_type for segment in params.segments]
        base_names = [random.choice(self.workout_names[wt]).split()[0] for wt in workout_types]
        combined_name = "Mixed_" + "_".join(base_names)
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{timestamp}_{combined_name}_{params.total_duration_minutes}min"

    def create_workout_description(self, params: WorkoutParameters) -> str:
        """Create a meaningful workout description for mixed workout"""
        description = "Mixed workout combining:\n"
        for segment in params.segments:
            intensity_range = self.intensity_ranges[segment.workout_type]
            description += f"- {segment.workout_type.value.title()} ({segment.duration_minutes}min): "
            description += f"{intensity_range[0]}-{intensity_range[1]}% of FTP\n"
        description += f"\nTotal Duration: {params.total_duration_minutes} minutes"
        return description



    def create_filename(self, workout_name: str, file_type: str = "mrc") -> str:
        """Create a properly formatted filename"""
        # Replace spaces with underscores and remove special characters
        clean_name = "".join(c if c.isalnum() or c in "._- " else "" for c in workout_name)
        clean_name = clean_name.replace(" ", "_")
        return f"{clean_name}.{file_type}"

    def generate_workout(self, params: WorkoutParameters) -> List[WorkoutInterval]:
        intervals = []
        current_time = 0
        duration_seconds = params.total_duration_minutes * 60

        # Always start with a 5-minute warmup at 40%
        warmup_duration = 300
        intervals.append(WorkoutInterval(0, warmup_duration, 40))
        current_time = warmup_duration

        # Generate intervals for each segment
        remaining_time = duration_seconds - 600  # Accounting for warmup and cooldown
        for segment in params.segments:
            segment_duration_seconds = int((segment.duration_minutes / params.total_duration_minutes) * remaining_time)
            segment_end_time = current_time + segment_duration_seconds

            while current_time < segment_end_time:
                if segment.workout_type == WorkoutType.SPRINTS:
                    # Special handling for sprints: include recovery
                    sprint_duration = random.randint(15, 30)
                    recovery_duration = random.randint(60, 180)

                    if current_time + sprint_duration + recovery_duration > segment_end_time:
                        break

                    sprint_power = random.randint(
                        self.intensity_ranges[segment.workout_type][0],
                        self.intensity_ranges[segment.workout_type][1]
                    )

                    intervals.append(WorkoutInterval(
                        current_time,
                        current_time + sprint_duration,
                        sprint_power
                    ))

                    intervals.append(WorkoutInterval(
                        current_time + sprint_duration,
                        current_time + sprint_duration + recovery_duration,
                        50  # Recovery at 50%
                    ))

                    current_time += sprint_duration + recovery_duration
                else:
                    # Regular interval generation
                    interval_duration = random.randint(
                        *self.interval_durations[segment.workout_type]
                    )

                    if current_time + interval_duration > segment_end_time:
                        interval_duration = segment_end_time - current_time

                    power = random.randint(
                        self.intensity_ranges[segment.workout_type][0],
                        self.intensity_ranges[segment.workout_type][1]
                    )

                    intervals.append(WorkoutInterval(
                        current_time,
                        current_time + interval_duration,
                        power
                    ))

                    current_time += interval_duration

        # Add cooldown at 40%
        intervals.append(WorkoutInterval(
            current_time,
            duration_seconds,
            40
        ))

        return intervals

    def calculate_metrics(self, intervals: List[WorkoutInterval]) -> Tuple[float, int]:
        """Calculate TSS for the workout"""
        total_tss = 0

        for interval in intervals:
            duration_hours = (interval.end_time - interval.start_time) / 3600
            intensity_factor = interval.power / 100  # Convert percentage to decimal
            tss = 100 * duration_hours * intensity_factor ** 2
            total_tss += tss

        return round(total_tss, 1)

    def export_mrc(self, intervals: List[WorkoutInterval], filename: str, description: str):
        """Export workout to MRC format with percentages of FTP"""
        with open(filename, 'w') as f:
            f.write("[COURSE HEADER]\n")
            f.write("VERSION = 2\n")
            f.write("UNITS = ENGLISH\n")
            f.write(f"DESCRIPTION = {description}\n")
            f.write(f"FILE NAME = {os.path.basename(filename)}\n")
            f.write("MINUTES PERCENT\n")
            f.write("[END COURSE HEADER]\n\n")

            f.write("[COURSE DATA]\n")
            for interval in intervals:
                # Convert seconds to minutes
                start_minutes = round(interval.start_time / 60, 2)
                end_minutes = round(interval.end_time / 60, 2)

                # Format with 2 decimal places for minutes
                f.write(f"{start_minutes:.2f}\t{interval.power}\n")
                f.write(f"{end_minutes:.2f}\t{interval.power}\n")
            f.write("[END COURSE DATA]\n")

    def export_zwo(self, intervals: List[WorkoutInterval], filename: str, workout_name: str = "Workout",
                   author: str = "Unknown"):
        """
        Exports a list of WorkoutInterval objects to a .zwo file.

        Args:
            intervals (List[WorkoutInterval]): List of workout intervals.
            filename (str): The name of the output .zwo file.
            workout_name (str): Name of the workout.
            author (str): Author of the workout.
        """
        # Create root element
        root = ET.Element("workout_file")

        # Add metadata
        name_elem = ET.SubElement(root, "name")
        name_elem.text = workout_name

        author_elem = ET.SubElement(root, "author")
        author_elem.text = author

        description_elem = ET.SubElement(root, "description")
        description_elem.text = f"Generated by workoutgen"

        # Add workout steps
        workout_elem = ET.SubElement(root, "workout")
        for interval in intervals:
            if interval.interval_type == "steady_state":
                ET.SubElement(workout_elem, "SteadyState", Duration=str(interval.duration), Power=str(interval.power))
            elif interval.interval_type == "intervals":
                ET.SubElement(workout_elem, "IntervalsT", Repeat=str(interval.repeat),
                              OnDuration=str(interval.on_duration), OffDuration=str(interval.off_duration),
                              OnPower=str(interval.on_power), OffPower=str(interval.off_power))

        # Write to file
        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

