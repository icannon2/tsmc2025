import matplotlib.pyplot as plt
import catppuccin
import matplotlib as mpl
import matplotlib.pyplot as plt
import json
import pandas as pd

from src.datasource import SQLRunner

output_folder = "charts"

mpl.style.use(catppuccin.PALETTE.mocha.identifier)


def plot_chart(json_data, runner: SQLRunner, name: str):
    """Generate line charts for each financial stat"""
    import os

    os.makedirs(output_folder, exist_ok=True)

    chart = json.loads(json_data)

    res = runner.execute_stmt(chart.get("sql"))
    if res.error_message:
        print(f"Error: {res.error_message}")
        return

    df = res.result.df()

    # Create figure
    # plt.figure(figsize=(10, 6))

    chart_type = chart.get("type")
    if chart_type == "line":
        # one stat many company or one company many stat
        colors = plt.rcParams["axes.prop_cycle"].by_key()[
            "color"
        ]  # Get default color cycle

        x_values = sorted(set(df["time"]))

        labels = []
        multiple_company = True
        if len(set(df["metric"])) < len(set(df["company"])):
            labels = sorted(set(df["company"]))
        else:
            labels = sorted(set(df["metric"]))
            multiple_company = False

        i = 0
        for label in labels:
            y_values = []
            if multiple_company:
                y_values = df[df["company"] == label]["value"].tolist()
            else:
                y_values = df[df["metric"] == label]["value"].tolist()

            plt.plot(
                x_values,
                y_values,
                marker="o",
                linestyle="-",
                color=colors[i % len(colors)],
                label=label,
            )
            i += 1

        plt.title(chart.get("title"))
        if chart.get("x-axis-label"):
            plt.xlabel(chart.get("x-axis-label"))
        if chart.get("y-axis-label"):
            plt.ylabel(chart.get("y-axis-label"))
        if chart.get("legend-title"):
            plt.legend(title=chart.get("legend-title"))
        else:
            plt.legend()

    elif chart_type == "bar":
        # todo: multiple x_values(different company), y_values = times, label = {company name}
        # single bar / double bar
        x_values = sorted(set(chart.get("x")))
        labels = chart.get("label")
        for i, label in labels:
            y_values = df[df["label"] == label]
            plt.bar(x_values, y_values, color="green", label="label")
        plt.xlabel(chart.get("x-axis-label"))
        plt.ylabel(chart.get("y-axis-label"))
        plt.title(chart.get("title"))

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

    chart_path = os.path.join(output_folder, name)
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
#       WHEN CalendarQuater = 1 THEN 'Q1'
#       WHEN CalendarQuater = 2 THEN 'Q2'
#       WHEN CalendarQuater = 3 THEN 'Q3'
#       WHEN CalendarQuater = 4 THEN 'Q4'
#       ELSE 'Unknown'
#   END  ' '  CAST(CalendarYear AS TEXT) as x,
#   USD_Value as y,
#     '营收' as label
#   FROM
#   financial_metrics
#   WHERE
#   "Company Name" = 'TSMC' AND CalendarYear = 2021 and Index = 'Revenue'
#   </sql>
# </chart>
# """

#     # Parse labels
#     result = parse_multiple_tags(content, "type", "sql")
#     print(result)

#     # for entry in result:
#     #     # Generate charts
#     #     plot_chart(times, entry['sql'], entry['type'])
