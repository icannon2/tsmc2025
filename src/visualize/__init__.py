from bot import DiscordBot

"""
An abstract class for media to be rendered.

Common media types: text, image, embed.
"""


class Media:
    def render(self, bot: DiscordBot):
        # This is a violation of the SOLID principle(bot argument). use DIP instead.
        pass

"""
A collection of media to be visualized.
"""
class Visualization:
    data: list[Media]


"""
An abstract class for module to visualizing the data.
"""


class VisualizeEffect:
    def __init__(self):
        pass

    """
    Attempt to match the visualization and replace it with the new one.

    For example, a chart visualization will find any text media that contains <chart/> data
    and extract part of text media(split if needed), replace it with the actual chart image.
    """

    def matchAndReplace(self, visualization: Visualization):
        pass

# Add visialization to the list here
visualizations = []