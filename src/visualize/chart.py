from ..datasource import SQLRunner, View
import matplotlib.pyplot as plt
import catppuccin
import matplotlib as mpl
import re

mpl.style.use(catppuccin.PALETTE.mocha.identifier)


def parse_multiple_tags(text, tag1, tag2):
    """
    Extracts multiple pairs of tag1 and tag2 from a given text.

    :param text: The full input string containing XML-like tags.
    :param tag1: The first tag name (e.g., "type").
    :param tag2: The second tag name (e.g., "sql").
    :return: A list of dictionaries, each containing content for tag1 and tag2.
    """
    pattern = rf"<{tag1}>(.*?)</{tag1}>.*?<{tag2}>(.*?)</{tag2}>"
    matches = re.findall(pattern, text, re.DOTALL)  # Find all non-overlapping matches

    # Convert to a list of dictionaries
    return [{"type": m[0].strip(), "sql": m[1].strip()} for m in matches]


def plot_charts(command, Type, times, output_folder="charts"):
    """Generate line charts for each financial stat"""
    import os

    os.makedirs(output_folder, exist_ok=True)

    result = runner.execute_stmt(command)
    if result.error_message:
        print(f"Error: {result.error_message}")
        return

    mapped_data = [result.map_row(row) for row in result.result.fetchall()]

    if not mapped_data:
        print("No data to plot!")
        return

    # Extract X and Y values from mapped_data
    # todo: extract data so that it's easy to draw
    x_values = [row["x"] for row in mapped_data]
    y_values = [row["y"] for row in mapped_data]

    # Create figure
    plt.figure(figsize=(10, 6))

    if chart_type == "line":
        # todo: multiple x_values(different company), y_values = times, label = {company name}
        plt.plot(
            x_values, y_values, marker="o", linestyle="-", color="b", label="Data Trend"
        )
        # todo: xlabel = time, ylabel = {stat name}(eg: tax expense), title = line chart of {stat name}
        plt.xlabel("X-Axis")
        plt.ylabel("Y-Axis")
        plt.title("Line Chart")
        plt.legend()

    elif chart_type == "bar":
        # todo: multiple x_values(different company), y_values = times, label = {company name}
        plt.bar(x_values, y_values, color="green", label="label")
        # todo: xlabel = time, ylabel = {stat name}(eg: tax expense), title = line chart of {stat name}
        plt.xlabel("X-Axis")
        plt.ylabel("Y-Axis")
        plt.title("Bar Chart")

    elif chart_type == "pie":
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

    chart_path = f"{output_folder}/graph.png"
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


if __name__ == "__main__":
    views = [
        View("FIN_Data", "SELECT * FROM FIN_Data.csv"),
        View("TRANSCRIPT_Data", "SELECT * FROM TRANSCRIPT_Data.csv"),
        View("TRANSCRIPT_File", "SELECT * FROM 'TRANSCRIPT File'"),
    ]
    runner = SQLRunner("data/datasource.duckdb", views)

    content = ""

    # Parse labels
    result = parse_multiple_tags(content, "type", "sql")

    for entry in result:
        # Generate charts
        plot_charts(times, entry["sql"], entry["type"])
