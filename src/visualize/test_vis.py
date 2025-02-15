from visualize import Visualizer

command = ""

v = Visualizer(None)
v.process_message(
    """title": "TSMC Revenue Trend (2023)",
"type": "line",
"x-axis-label": "Quarter",
"y-axis-label": "Revenue (USD millions)",
"sql": "SELECT CALENDAR_QTR AS qtr, "Revenue" AS y FROM FIN_Data WHERE "CompanyName" = 'TSMC' AND "CALENDAR_YEAR" = 2023",
"labels": [
"Q1",
"Q2",
"Q3",
"Q4"
]""",
    None,
)
