import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import base64
import io
from datetime import datetime
import json
from enduWorkoutGen.workoutgen import WorkoutGenerator, WorkoutParameters, WorkoutType, WorkoutSegment

class WorkoutDashboard:
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.workout_generator = WorkoutGenerator()
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Workout Generator Dashboard", className="text-center mb-4")
                ])
            ]),

            # Workout Configuration Section
            dbc.Card([
                dbc.CardHeader(html.H3("Workout Configuration")),
                dbc.CardBody([
                    # Total Duration
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Total Duration (minutes):"),
                            dcc.Slider(
                                id='total-duration',
                                min=20,
                                max=180,
                                step=5,
                                value=60,
                                marks={i: str(i) for i in range(20, 181, 20)},
                                className="mb-4"
                            ),
                        ])
                    ]),

                    # Segment Configuration
                    html.Div([
                        html.H4("Workout Segments"),
                        dbc.Button(
                            "Add Segment",
                            id="add-segment",
                            color="primary",
                            className="mb-3"
                        ),
                        html.Div(id="segments-container", children=[]),
                    ]),

                    # Generate Button
                    dbc.Button(
                        'Generate Workout',
                        id='generate-button',
                        color="success",
                        className="mt-3"
                    ),
                ])
            ], className="mb-4"),

            # Workout Display Section
            dbc.Card([
                dbc.CardHeader(html.H3("Generated Workout")),
                dbc.CardBody([
                    # Workout Info
                    html.Div(id='workout-info', children=[]),

                    # Workout Graph
                    html.Div(id='graph-container', style={'display': 'none'}, children=[
                        dcc.Graph(id='workout-graph')
                    ]),

                    # Download Button
                    dbc.Button(
                        "Download Workout",
                        id="download-button",
                        color="info",
                        className="mt-3",
                        style={'display': 'none'}
                    ),
                    dcc.Download(id="download-workout")
                ])
            ])

        ], fluid=True)

    def setup_callbacks(self):
        @self.app.callback(
            Output('segments-container', 'children'),
            [Input('add-segment', 'n_clicks')],
            [State('segments-container', 'children')],
            prevent_initial_call=True
        )
        def update_segments(n_clicks, existing_segments):
            if n_clicks is None:
                return []

            if existing_segments is None:
                existing_segments = []

            segment_index = len(existing_segments)

            new_segment = dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Workout Type:"),
                            dcc.Dropdown(
                                options=[{'label': wt.value.title(), 'value': wt.value}
                                         for wt in WorkoutType],
                                value=WorkoutType.ENDURANCE.value,
                                id={'type': 'segment-type', 'index': segment_index}
                            ),
                        ], width=8),
                        dbc.Col([
                            dbc.Label("Duration (minutes):"),
                            dcc.Slider(
                                min=5,
                                max=120,
                                step=5,
                                value=15,
                                marks={i: str(i) for i in range(0, 121, 15)},
                                id={'type': 'segment-duration', 'index': segment_index}
                            ),
                        ], width=4),
                    ])
                ])
            ], className="mb-3")

            return existing_segments + [new_segment]

        @self.app.callback(
            [Output('workout-graph', 'figure'),
             Output('workout-info', 'children'),
             Output('download-button', 'style'),
             Output('graph-container', 'style'),
             Output('download-button', 'n_clicks')],
            Input('generate-button', 'n_clicks'),
            [State('total-duration', 'value'),
             State('segments-container', 'children')],
            prevent_initial_call=True
        )
        def generate_workout(n_clicks, total_duration, segments):
            if not segments:
                raise PreventUpdate

            # Parse segments
            workout_segments = []
            for segment in segments:
                # Extract workout type and duration from the segment structure
                card_body = segment['props']['children'][0]['props']['children']
                row = card_body[0]['props']['children']

                # Get workout type from first column
                workout_type_dropdown = row[0]['props']['children'][1]
                segment_type = workout_type_dropdown['props']['value']

                # Get duration from second column
                duration_slider = row[1]['props']['children'][1]
                segment_duration = duration_slider['props']['value']

                workout_segments.append(
                    WorkoutSegment(WorkoutType(segment_type), segment_duration)
                )

            # Generate workout
            params = WorkoutParameters(segments=workout_segments, total_duration_minutes=total_duration)
            intervals = self.workout_generator.generate_workout(params)

            # Create figure
            fig = go.Figure()
            x_values = []
            y_values = []

            for interval in intervals:
                x_values.extend([interval.start_time / 60, interval.end_time / 60])
                y_values.extend([interval.power, interval.power])

            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines',
                name='Power'
            ))

            fig.update_layout(
                title='Workout Profile',
                xaxis_title='Time (minutes)',
                yaxis_title='Power (% FTP)',
                showlegend=True,
                template='plotly_white'
            )

            # Calculate metrics
            tss = self.workout_generator.calculate_metrics(intervals)

            # Create workout info
            workout_name = self.workout_generator.generate_workout_name(params)
            description = self.workout_generator.create_workout_description(params)

            info_div = html.Div([
                html.H4(workout_name, className="mb-3"),
                html.P(description, className="text-muted"),
                html.P(f"Training Stress Score (TSS): {tss}", className="fw-bold")
            ])

            # Store workout data for download
            self.current_workout = {
                'intervals': intervals,
                'name': workout_name,
                'description': description
            }

            return fig, info_div, {'display': 'block'}, {'display': 'block'}, None

        @self.app.callback(
            Output("download-workout", "data"),
            Input("download-button", "n_clicks"),
            prevent_initial_call=True
        )
        def download_workout(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            if not hasattr(self, 'current_workout'):
                raise PreventUpdate

            # Create a temporary file
            from tempfile import NamedTemporaryFile
            import os

            with NamedTemporaryFile(mode='w', delete=False, suffix='.mrc') as temp_file:
                # Export to temporary file
                self.workout_generator.export_mrc(
                    self.current_workout['intervals'],
                    temp_file.name,
                    self.current_workout['description']
                )

                # Read the contents
                with open(temp_file.name, 'r') as f:
                    content = f.read()

                # Clean up
                os.unlink(temp_file.name)

            return dict(
                content=content,
                filename=f"{self.current_workout['name']}.mrc"
            )
    def run_server(self, debug=True):
        self.app.run_server(host="0.0.0.0",port=8050,debug=debug)