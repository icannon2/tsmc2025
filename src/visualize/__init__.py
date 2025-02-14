import uuid
import discord
from abc import ABC
from ..datasource import SQLRunner
from .chart import plot_chart
from discord import TextChannel, File
import re
import os

"""
An abstract class for media to be rendered.

Common media types: text, image, embed.
"""

output_folder = "charts"


class Media:
    text: str | None
    # base64 png image
    image: File | None

    def __init__(self, text: str | None = None, image: File | None = None):
        if text is None:
            self.image = image
            self.text = None
        else:
            self.image = None
            self.text = text

    def is_text(self) -> bool:
        return self.text is not None

    async def render(self, channel: TextChannel):
        if self.text is not None and len(self.text.strip()) != 0:
            await channel.send(self.text)
        elif self.image is not None:
            await channel.send(file=self.image)


"""
A collection of media to be visualized.
"""


class Visualization:
    data: list[Media]

    def __init__(self, text: str | None = None):
        self.data = []
        if text is not None:
            self.data.append(Media(text=text))

    async def render(self, channel: TextChannel):
        for media in self.data:
            await media.render(channel)


class VisualizeEffect(ABC):
    sql_runner: SQLRunner

    """
    An abstract class for module to visualizing the data.
    """

    def __init__(self, sql_runner: SQLRunner):
        pass

    def matchAndReplace(self, visualization: Visualization):
        """
        Attempt to match the visualization and replace it with the new one.

        For example, a chart visualization will find any text media that contains <chart/> data
        and extract part of text media(split if needed), replace it with the actual chart image.
        """
        pass

class ChartEffect(VisualizeEffect):
    sql_runner: SQLRunner

    def __init__(self, sql_runner: SQLRunner):
        self.sql_runner = sql_runner

    def matchAndReplace(self, visualization: Visualization):
        chartRegex = "<chart>([\s\S]*?)<\/chart>"
        new_data = []

        for media in visualization.data:
            if not media.is_text():
                new_data.append(media)
                continue

            raw_parts = re.split(chartRegex, media.text) if media.text else []
            raw_matches = re.findall(chartRegex, media.text) if media.text else []
            parts = [part.strip() for part in raw_parts if part and part.strip()]
            matches = [match.strip() for match in raw_matches if match and match.strip()]

            for p in parts:
                print(p)
            print("------------")
            for m in matches:
                print(m)

            for part in parts:
                if not part: continue
                if part in matches: # Add chart
                    try:
                        loc = uuid.uuid4()
                        plot_chart(part, self.sql_runner, f"{loc}.png")
                        graph_path = os.path.join(output_folder, f"{loc}.png")
                        img_file = discord.File(graph_path, filename=f"{loc}.png")
                        new_data.append(Media(image=img_file))
                    except Exception as e:
                        new_data.append(Media(text=f"Error: {e}"))
                        print(e)
                else:
                    new_data.append(Media(text=part))

        visualization.data = new_data


class Visualizer:
    def __init__(self, sql_runner: SQLRunner):
        self.effects = [ChartEffect(sql_runner)]

    async def process_message(self, message: str, channel: TextChannel):
        """
        Process a message and render the visualization in the channel.

        Args:
            message (str): The message to process
            channel (TextChannel): The Discord channel to render to
        """
        # Create initial visualization with the message
        visualization = Visualization()
        visualization.data = [Media(text=message)]

        # Apply all effects
        for effect in self.effects:
            effect.matchAndReplace(visualization)

        # Render the final visualization
        await visualization.render(channel)
