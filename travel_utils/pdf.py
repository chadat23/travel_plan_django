from typing import Optional, Any

from fpdf import fpdf
from PIL import ImageFont


class PDF(fpdf.FPDF):
    """
    A PDF, inherited from fpdf2 fpdf.FPDF
    :param orientation: the orientation of the page
    :type orientation: str
    :param unit: the unit of measure of the page cells
    :type unit: str
    :param format: the size of the pages to be used
    :type format: str
    """

    def __init__(self, orientation='P', unit='mm', format='A4'):

        super().__init__(orientation=orientation, unit=unit, format=format)

        # default height of a pdf cell
        self.height = 6

        # RGB values for the background colors of cells
        self.gray = (200, 200, 200)
        self.green = (0, 210, 0)
        self.amber = (255, 191, 0)
        self.red = (255, 100, 100)

    def add_cell(self, w: int, txt: str = '', roll: str = 'V', 
                 border: int = 0, ln: int = 0, align: str = '', fill: int = 0, link: str = '',
                 font_size: int = None, height: int = 0):
        """
        Fits and formats the text to the cell that it's supposed to fit into.
        View fpdf2's cell method for additional info on how to use various parameters.
        
        :param w: width of the cell in mm.
        :type w: int
        :param txt: the string that is to be put in the cell
        :type txt: str
        :param roll: specifies whether the text is a Label or Value: "L" or "V" is expected
        :type roll: str
        :param wrap: Whether or not the text should wrap within the cell.
        :type wrap: bool
        :param border: whether or not the cell should have a borderline. 1 for yes, 2 for no.
        :type border: int
        :param ln: 1 if the line should be rapped after the current cell, 0 if not
        :type ln: int
        :param align: how text should be aligned within the cell; "L" for left, "C" for centered
        :type align: str
        :param fill: whether or not the cell should have a background color
        :type fill: int
        :param link: a hyperlink
        :type link: str
        :param font_size: the font size of the cell's text in points
        :type font_size: int
        :param height: the height of the cell in mm
        :type height: int
        """

        if not txt:
            txt = ''

        if not height:
            height = self.height

        if font_size:
            _font_size = font_size

        if roll.strip().lower() == 'l':
            _font_style = 'B'
            self.set_fill_color(*self.gray)
            fill = 1
            if not font_size:
                _font_size = 8
        elif roll.strip().lower() == 'v':            
            _font_style = ''
            if not font_size:
                _font_size = 5
                for size in range(10, 5, -1):
                    font = ImageFont.truetype('arial.ttf', size)
                    width = font.getsize(txt)[0]/75*25.4
                    if width < w - 2:
                        _font_size = size
                        break

        self.set_font('Arial', _font_style, size=_font_size)

        self.cell(w, height, txt, border, ln, align, fill, link)

