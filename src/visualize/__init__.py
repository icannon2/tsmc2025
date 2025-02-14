from bot import DiscordBot
from abc import ABC
from ..datasource import SQLRunner, View
from .chart import plot_chart
from discord import TextChannel, File
import re

"""
An abstract class for media to be rendered.

Common media types: text, image, embed.
"""

graph_path = ""


class Media:
    text: str | None
    # base64 png image
    image: File | None

    def __init__(self, text: str | None = None, image: File | None = None):
        self.text = text
        if self.text is None:
            self.image = image

    def is_text(self) -> bool:
        return not self.text is None

    def render(self, channel: TextChannel):
        if self.text is not None:
            channel.send(self.text)
        elif self.image is not None:
            channel.send(self.image)


"""
A collection of media to be visualized.
"""


class Visualization:
    data: list[Media]

    def render(channel: TextChannel):
        for media in self.data:
            media.render(channel)


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
        for media in visialization.data:
            if not media.is_text():
                continue
            chartRegex = "<chart>([\s\S]*?)<\/chart>"

            matches = re.findall(chartRegex, media.text)
            textSplit = iter(re.split(chartRegex, media.text))

            visialization.data = []

            for match in matches:
                visialization.data.append(Media(text=next(textSplit)))
                plot_chart(match)

                img_bytes = BytesIO()
                img_file = discord.File(img_bytes, graph_path)
                os.remove(graph_path)
                # store graph in one place and remove it immediately after use
                visialization.data.append(Media(image=img_file))

            visialization.data.append(next(textSplit))
