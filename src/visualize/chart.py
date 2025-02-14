from ..datasource import SQLRunner, View
import matplotlib.pyplot as plt
import catppuccin
import matplotlib as mpl
import json
import pandas as pd

import re

output_folder = "charts"

mpl.style.use(catppuccin.PALETTE.mocha.identifier)


def plot_chart(json_data):
    """Generate line charts for each financial stat"""
    import os

    os.makedirs(output_folder, exist_ok=True)

    chart = json.loads(json_data)

    result = runner.execute_stmt(chart.get("sql"))
    if result.error_message:
        print(f"Error: {result.error_message}")
        return

    df = pd.DataFrame([result.map_row(row) for row in result.result.fetchall()])

    if not df:
        print("No data to plot!")
        return

    # Create figure
    plt.figure(figsize=(10, 6))

    chart_type = chart.get("type")
    if chart_type == "line":
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']  # Get default color cycle

        x_values = sorted(set(chart.get('x')))
        labels = chart.get('label')
        for i, label in labels:
            y_values = df[df['label'] == label]
            plt.plot(
                x_values, y_values, marker="o", linestyle="-", color=colors[i % len(colors)], label=label
            )
        plt.xlabel(chart.get('x-axis-label'))
        plt.ylabel(chart.get('y-axis-label'))
        plt.title(chart.get('title'))
        plt.legend(title=chart.get('legend-title'))

    elif chart_type == "bar":
        # todo: multiple x_values(different company), y_values = times, label = {company name}
        # single bar / double bar
        x_values = sorted(set(chart.get('x')))
        labels = chart.get('label')
        for i, label in labels:
            y_values = df[df['label'] == label]
            plt.bar(x_values, y_values, color="green", label="label")
        plt.xlabel(chart.get('x-axis-label'))
        plt.ylabel(chart.get('y-axis-label'))
        plt.title(chart.get('title'))

    elif chart_type == "pie":
        # temporarily ignored
        plt.pie(
            y_values,
            labels=x_values,
            autopct="%1.1f%%",
            startangle=140,
            colors=["blue", "red", "green", "orange"],
        )
        plt.title("Pie Chart")

    else:
        print("Invalid chart type! Please use 'bar', 'pie', or 'line'.")
        return

    # Show the chart
    plt.grid(True) if chart_type in ["line", "bar"] else None

    chart_path = os.path.join(output_folder, f"graph.png")
    plt.savefig(chart_path)
    plt.close()

    # for stat, df in data_dict.items():
    #     plt.figure(figsize=(10, 5))

    #     # Ensure the data is sorted by time
    #     df = df.set_index("season").reindex(times).reset_index()

    #     # Plot each company’s data
    #     for company in df.columns[1:]:  # Skip "season" column
    #         plt.plot(df["season"], df[company], marker="o", linestyle="-", label=company)

    #     plt.xlabel("Season")
    #     plt.ylabel(stat)
    #     plt.title(f"Trends of {stat} Over Time")
    #     plt.legend()
    #     plt.grid(True)
    #     plt.xticks(rotation=45)
    #     plt.tight_layout()

    #     # Save the chart
    #     chart_path = f"{output_folder}/{stat.replace(' ', '_')}.png"
    #     plt.savefig(chart_path)
    #     plt.close()

    #     print(f"Saved: {chart_path}")


# if __name__ == "__main__":
#     views = [
#         View("FIN_Data", "SELECT * FROM FIN_Data.csv"),
#         View("TRANSCRIPT_Data", "SELECT * FROM TRANSCRIPT_Data.csv"),
#         View("TRANSCRIPT_File", "SELECT * FROM 'TRANSCRIPT File'"),
#     ]
#     runner = SQLRunner("data/datasource.duckdb", views)

#     content = """<chart>
#   <title>台积电2021年季度营收 (亿美元)</title>
#   <type>line</type>
#   <sql>
#   SELECT
#   CASE
#       WHEN CALENDAR_QTR = 1 THEN 'Q1'
#       WHEN CALENDAR_QTR = 2 THEN 'Q2'
#       WHEN CALENDAR_QTR = 3 THEN 'Q3'
#       WHEN CALENDAR_QTR = 4 THEN 'Q4'
#       ELSE 'Unknown'
#   END  ' '  CAST(CALENDAR_YEAR AS TEXT) as x,
#   USD_Value as y,
#     '营收' as label
#   FROM
#   financial_metrics
#   WHERE
#   "Company Name" = 'TSMC' AND CALENDAR_YEAR = 2021 and Index = 'Revenue'
#   </sql>
# </chart>
# """

#     # Parse labels
#     result = parse_multiple_tags(content, "type", "sql")
#     print(result)

#     # for entry in result:
#     #     # Generate charts
#     #     plot_chart(times, entry['sql'], entry['type'])
