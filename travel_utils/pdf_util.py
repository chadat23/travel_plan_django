import os
from typing import Tuple

from .pdf import PDF
from travel.models import Travel, TravelUserUnit


def make_and_save_pdf(travel: Travel, name: str, path: str):
    """
    Generates and saves a PDF based on a travel object.
    :param travel: the travel object to be modeled as a PDF
    :type travel: Travel
    :param name: the name that's to be used when saving the file.
    The file extension, ".pdf" does not need to be included.
    :type name: str
    :param path: the folder location where the file's to be saved
    :type path: str
    :return: None
    """
    pdf = _generate_pdf(travel)
    _save_file(pdf, name, path)


def _save_file(pdf: PDF, name: str, path: str) -> str:
    """
    Saves a PDF file.
    :param pdf: the pdf file to be saved
    :type pdf: PDF
    :param name: the name that's to be used when saving the file
    :type name: str
    :param path: the folder location where the file's to be saved
    :type path: str
    :return: str
    """
    if name[:-4] != '.pdf':
        name += '.pdf'
    working_directory = os.getcwd()
    try:
        os.chdir(path)
        pdf.output(name)
    finally:
        os.chdir(working_directory)


def _generate_pdf(travel: Travel) -> PDF:
    """
    Creates a pdf file.
    :param travel: the travel plan that the pdf's to be based on
    :type travel: Travel
    :return: PDF
    """

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    pdf.add_cell(22, 'Start Date:', 'L', 1, 0, 'C')
    pdf.add_cell(55, 'Entry Point:', 'L', 1, 0, 'C')
    pdf.add_cell(22, 'End Date:', 'L', 1, 0, 'C')
    pdf.add_cell(55, 'Exit Point:', 'L', 1, 0, 'C')
    pdf.add_cell(15, 'Tracked:', 'L', 1, 0, 'C')
    pdf.add_cell(20, 'PLB #:', 'L', 1, 1, 'C')

    pdf.add_cell(22, str(travel.start_date), 'V', 1, 0, 'L')
    pdf.add_cell(55, travel.entry_point.name, 'V', 1, 0, 'L')
    pdf.add_cell(22, str(travel.end_date), 'V', 1, 0, 'L')
    pdf.add_cell(55, travel.exit_point.name, 'V', 1, 0, 'L')
    pdf.add_cell(15, 'Yes' if travel.tracked else 'No', 'V', 1, 0, 'L')
    pdf.add_cell(20, travel.plb, 'V', 1, 1, 'L')

    pdf.cell(10, 2, '', ln=1)

    pdf.add_cell(49, 'Name:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Radio Call Sign:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Pack Color:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Tent Color:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Fly/Tarp Color:', 'L', 1, 1, 'C')

    # find the trip leader TravelUserUnit that's the trip leader and separate it from the other travelers
    for unit in travel.traveluserunit_set.all():
        if unit.traveler.username == travel.trip_leader.username:
            leader_unit = unit
            other_units = list(travel.traveluserunit_set.all())
            other_units.remove(leader_unit)
            break
    _write_traveler(pdf, leader_unit)
    for unit in other_units:
        _write_traveler(pdf, unit)

    pdf.cell(10, 2, '', ln=1)

    pdf.add_cell(22, 'Date:', 'L', 1, 0, 'C')
    pdf.add_cell(46, 'Starting Point:', 'L', 1, 0, 'C')
    pdf.add_cell(46, 'Ending Point:', 'L', 1, 0, 'C')
    pdf.add_cell(40, 'Route:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Mode:', 'L', 1, 1, 'C')

    for day in sorted(travel.traveldayplan_set.all()):
        pdf.add_cell(22, str(day.date), 'V', 1, 0, 'L')
        pdf.add_cell(46, day.starting_point.name, 'V', 1, 0, 'L')
        pdf.add_cell(46, day.ending_point.name, 'V', 1, 0, 'L')
        pdf.add_cell(40, day.route, 'V', 1, 0, 'L')
        pdf.add_cell(35, day.mode, 'V', 1, 1, 'L')

    pdf.cell(10, 2, '', ln=1)

    pdf.add_cell(22, 'Plate:', 'L', 1, 0, 'C')
    pdf.add_cell(46, 'Make:', 'L', 1, 0, 'C')
    pdf.add_cell(46, 'Model:', 'L', 1, 0, 'C')
    pdf.add_cell(40, 'Color:', 'L', 1, 0, 'C')
    pdf.add_cell(35, 'Location:', 'L', 1, 1, 'C')

    if travel.vehicle:
        plate = travel.vehicle.plate
        make = travel.vehicle.make
        model = travel.vehicle.model
        if travel.vehicle.color:
            color = travel.vehicle.color.name
        else:
            color = ''
        location = travel.vehicle_location        
    else:
        plate = ''
        make = ''
        model = ''
        color = ''
        location = ''
    pdf.add_cell(22, plate, 'V', 1, 0, 'L')
    pdf.add_cell(46, make, 'V', 1, 0, 'L')
    pdf.add_cell(46, model, 'V', 1, 0, 'L')
    pdf.add_cell(40, color, 'V', 1, 0, 'L')
    pdf.add_cell(35, location, 'V', 1, 1, 'L')

    pdf.cell(10, 2, '', ln=1)
    y = pdf.get_y()

    equip_font_size = 8
    width1 = 7
    width2 = 26
    pdf.add_cell(99, 'Equipment:', 'L', 1, 0, 'C')
    pdf.add_cell(30, 'Weapon:', 'L', 1, 0, 'C')
    pdf.add_cell(30, 'Days Worth of Food:', 'L', 1, 0, 'C')
    pdf.add_cell(30, 'Time You Monitor Radio:', 'L', 1, 1, 'C', font_size=7)
    pdf.add_cell(width1, 'X' if travel.bivy_gear else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Bivy Gear', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.head_lamp else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Head Lamp', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.rope else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Rope', 'V', 0, 0, 'L')
    pdf.add_cell(30, travel.weapon, 'V', 1, 0, 'C')
    pdf.add_cell(30, str(travel.days_of_food), 'V', 1, 0, 'C')
    pdf.add_cell(30, travel.radio_monitor_time, 'V', 1, 1, 'C')
    pdf.add_cell(width1, 'X' if travel.compass else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Compas', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.helmet else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Helmet', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.shovel else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Shovel', 'V', 0, 0, 'L')
    pdf.add_cell(30, 'Off-Trail Map Included?:', 'L', 1, 0, 'C', font_size=7)
    pdf.add_cell(30, 'Cell Phone #:', 'L', 1, 0, 'C')
    pdf.add_cell(30, 'Satellite Phone #:', 'L', 1, 1, 'C', font_size=9)
    pdf.add_cell(width1, 'X' if travel.first_aid_kit else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'First Aid Kit', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.ice_axe else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Ice Axe', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.signal_mirror else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Signal Mirror', 'V', 0, 0, 'L')
    pdf.add_cell(30, 'Yes' if travel.off_trail_travel else 'No', 'V', 1, 0, 'C')
    pdf.add_cell(30, travel.cell_number, 'V', 1, 0, 'C')
    pdf.add_cell(30, travel.satellite_number, 'V', 1, 1, 'C')
    pdf.add_cell(width1, 'X' if travel.flagging else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Flagging', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.map else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Map', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.space_blanket else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Space Blanket', 'V', 0, 1, 'L')
    pdf.add_cell(width1, 'X' if travel.flare else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Flare', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.matches else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Matches', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.spare_battery else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Spare Battery', 'V', 0, 1, 'L')
    pdf.add_cell(width1, 'X' if travel.flashlight else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Flashlight', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.probe_pole else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Probe Pole', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.tent else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Tent', 'V', 0, 1, 'L')
    pdf.add_cell(width1, 'X' if travel.gps else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'GPS', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.radio else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Radio', 'V', 0, 0, 'L')
    pdf.add_cell(width1, 'X' if travel.whistle else '', 'V', 1, 0, 'L', font_size=equip_font_size)
    pdf.add_cell(width2, 'Whistle', 'V', 0, 1, 'L')

    pdf.cell(10, 2, '', ln=1)

    pdf.add_cell(41, 'Responsible Party Name:', 'L', 1, 0, 'C')
    pdf.add_cell(37, 'Email:', 'L', 1, 0, 'C')
    pdf.add_cell(37, 'Work Phone #:', 'L', 1, 0, 'C')
    pdf.add_cell(37, 'Home Phone #:', 'L', 1, 0, 'C')
    pdf.add_cell(37, 'Cell Phone #:', 'L', 1, 1, 'C')

    for c in travel.contacts.all():
        pdf.add_cell(41, c.username, 'V', 1, 0, 'L')
        pdf.add_cell(37, c.email, 'V', 1, 0, 'L')
        pdf.add_cell(37, c.profile.work_number, 'V', 1, 0, 'L')
        pdf.add_cell(37, c.profile.home_number, 'V', 1, 0, 'L')
        pdf.add_cell(37, c.profile.cell_number, 'V', 1, 1, 'L')

    pdf.cell(10, 2, '', ln=1)

    # This draws the boxes that the GAR labels will be put in.
    # Without this, boxes are draws at the same angle as the labels.
    x = pdf.get_x()
    y = pdf.get_y()
    gar_width = 15
    gar_height = 34
    for _ in range(10):
        pdf.add_cell(gar_width, ' ', 'L', 1, 0, fill=1, height=gar_height)

    gar_x = pdf.get_x()
    gar_y = pdf.get_y()

    pdf.set_font("Arial", 'B', size=8)
    _label(pdf, 'Team Member', x, y, 0, gar_height)
    _label(pdf, 'Supervision', x, y, 1, gar_height)
    _label(pdf, 'Planning', x, y, 2, gar_height)
    _label(pdf, 'Contingency Resources', x, y, 3, gar_height)
    _label(pdf, 'Communication', x, y, 4, gar_height)
    _label(pdf, 'Team Selection', x, y, 5, gar_height)
    _label(pdf, 'Team Fitness', x, y, 6, gar_height)
    _label(pdf, 'Environment', x, y, 7, gar_height)
    _label(pdf, 'Incident Complexity', x, y, 8, gar_height)
    _label(pdf, 'Team Member Total', x, y, 9, gar_height)

    pdf.set_xy(x, y + gar_height)
    _write_gar(pdf, 1, leader_unit, gar_width)
    for i, unit in enumerate(other_units):
        _write_gar(pdf, i + 2, unit, gar_width)

    gar_color_height = 5
    pdf.set_xy(gar_x, gar_y)
    pdf.set_fill_color(*pdf.green)
    pdf.add_cell(39, 'Green: 1-35', 'V', 1, 0, 'C', 1, height=gar_color_height)
    pdf.set_xy(gar_x, gar_y + gar_color_height)
    pdf.set_fill_color(*pdf.amber)
    pdf.add_cell(39, 'Amber: 36-60', 'V', 1, 0, 'C', 1, height=gar_color_height)
    pdf.set_xy(gar_x, gar_y + 2 * gar_color_height)
    pdf.set_fill_color(*pdf.red)
    pdf.add_cell(39, 'Red: 61-80', 'V', 1, 0, 'C', 1, height=gar_color_height)

    pdf.set_xy(gar_x, gar_y + 1 + 3 * gar_color_height)
    pdf.add_cell(39, 'Average Team Member Totals', 'L', 1, 1, 'C', font_size=7)
    pdf.set_xy(gar_x, gar_y + 1 + 3 * gar_color_height + pdf.height)
    pdf.set_fill_color(*_set_gar_color(pdf, travel.gar_average))
    pdf.add_cell(39, str(travel.gar_average), 'V', 1, 0, 'C', 1)
    pdf.set_xy(gar_x, gar_y + 1 + 3 * gar_color_height + 2 * pdf.height)
    pdf.add_cell(39, 'Mitigated GAR', 'L', 1, 0, 'C')
    pdf.set_xy(gar_x, gar_y + 1 + 3 * gar_color_height + 3 * pdf.height)
    pdf.set_fill_color(*_set_gar_color(pdf, travel.gar_mitigated))
    pdf.add_cell(39, str(travel.gar_mitigated), 'V', 1, 1, 'C', 1)

    pdf.set_y(gar_y + gar_height + 1 + pdf.height * (1 + len(other_units)))

    pdf.add_cell(95, 'Mitigations Taken', 'L', 1, 0, 'C', 1)
    pdf.add_cell(94, 'Additional Notes', 'L', 1, 1, 'C', 1)
    if travel.gar_mitigations:
        mitigations = travel.gar_mitigations
    else:
        mitigations = ''
    pdf.multi_cell(95, 4, mitigations, 1, 'L', 0)
    if travel.notes:
        notes = travel.notes
    else:
        notes = ''
    pdf.multi_cell(94, 4, notes, 1, 'L', 0)

    return pdf


def _write_traveler(pdf: PDF, unit):
    """
    Wright a portion of a TravelUserUnit to the PDF
    :param pdf: the PDF that's to be written to
    :type pdf: PDF
    :param unit: the TravelUserUnit to be written
    :return: None
    """
    if unit.traveler:
        pdf.add_cell(49, unit.traveler.username, 'V', 1, 0, 'L')
    else:
        pdf.add_cell(49, '', 'V', 1, 0, 'L')
    if unit.traveler.profile.call_sign:
        pdf.add_cell(35, unit.traveler.profile.call_sign, 'V', 1, 0, 'L')
    else:
        pdf.add_cell(35, '', 'V', 1, 0, 'L')
    if unit.pack_color:
        pdf.add_cell(35, unit.pack_color.name, 'V', 1, 0, 'L')
    else:
        pdf.add_cell(35, '', 'V', 1, 0, 'L')
    if unit.tent_color:
        pdf.add_cell(35, unit.tent_color.name, 'V', 1, 0, 'L')
    else:
        pdf.add_cell(35, '', 'V', 1, 0, 'L')
    if unit.fly_color:
        pdf.add_cell(35, unit.fly_color.name, 'V', 1, 1, 'L')
    else:
        pdf.add_cell(35, '', 'V', 1, 1, 'L')


def _label(pdf: PDF, label: str, x: int, y: int, ix: int, h: int):
    """
    Creates a label for the GAR info.
    :param pdf: the pdf that's to be written to
    :type pdf: PDF
    :param label: the text that's to be written into the label
    :type label: str
    :param x: the x location of the label that's to be written
    :type x: int
    :param y: the y locaiton of the label that's to be written
    :type y: int
    :param ix: the index of the particular label in the array of labels
    :type ix: int
    :param h: the height of the label to be made
    :type h: int
    :return: None
    """

    pdf.set_xy(x + ix * 15 - 7, y + h - 3)
    pdf.rotate(75)
    pdf.cell(20, 20, label, 0, 0, 'L')
    pdf.rotate(0)


def _write_gar(pdf: PDF, i: int, unit: TravelUserUnit, width: int):
    """
    Writes the GAR info for one traveler.
    :param pdf: the PDF to be written to
    :type pdf: PDF
    :param i: the index of the traveler
    :type i: int
    :param unit: the traveler unit that's to be written
    :type unit: TravelUserUnit
    :param width: the width of the cell to be written
    :type width: int
    :return: None
    """

    pdf.add_cell(width, str(i), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.supervision), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.planning), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.contingency), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.comms), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.team_selection), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.fitness), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.env), 'V', 1, 0, 'C')
    pdf.add_cell(width, str(unit.complexity), 'V', 1, 0, 'C')
    pdf.set_fill_color(*_set_gar_color(pdf, unit.total_gar_score()))
    pdf.add_cell(width, str(unit.total_gar_score()), 'V', 1, 1, 'C', 1)


def _set_gar_color(pdf, gar_score: int) -> Tuple[int, int, int]:
    """
    Set the background color in accordance to the GAR score.
    :param pdf: the PDF that's to be written to
    :type pdf: PDF
    :param gar_score: the GAR score that's to be referenced
    :type gar_score: int
    :return: Tuple[int, int, int]
    """

    if gar_score < 36:
        return pdf.green
    elif 35 < gar_score < 61:
        return pdf.amber
    else:
        return pdf.red