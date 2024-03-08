# coding: utf-8
from enum import Enum

from qfluentwidgets import FluentIconBase, getIconColor, Theme


class Icon(FluentIconBase, Enum):

    DATASHARING = "DataSharing"
    EMOJI_TAB_SYMBOLS = "EmojiTabSymbols"
    FACE = "Face"
    GRID = "Grid"
    MENU = "Menu"
    METADATA_CLEAN = "MetadataClean"
    MOSAIC = "Mosaic"
    PRICE = "Price"
    TEXT = "Text"
    
    

    def path(self, theme=Theme.AUTO):
        return f":/gallery/images/icons/{self.value}_{getIconColor(theme)}.svg"
