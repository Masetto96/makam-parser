from music21 import *
import xml.etree.ElementTree as ET

ALTER_VALUES = {
    'half-flat': (-1, 0),
    'slash-flat': (-4, 0),
    'double-slash-flat': (-8, 0),
    'flat': (-5, -1),
    'double-flat': (-9, 0),
    'half-sharp': (+1, 0),
    'sharp': (+4, +1),
    'slash-quarter-sharp': (+5, 0),
    'slash-sharp': (+8, 0),
    'double-sharp': (+9, 0),
}

TONE_DIVISION = 200 / 9

def _describe_key_signature(tree):
    """Print information about key signature in the score."""
    notes = []
    accidentals = []
    for k in tree.iter("key"):
        for ks in k.findall("key-step"):
            notes.append(ks.text)
        for ka in k.findall("key-accidental"):
            accidentals.append(ka.text)

    print("The key signature of this score has:")
    for i in range(len(notes)):
        print("-", notes[i], accidentals[i])


def _update_alter_values_in_xml(notes):
    """
    Update the alter values in the XML representation of the notes.

    Parameters:
        notes (list): A list of notes.

    Returns:
        set: A set of accidentals found in the notes.
    """
    # Set to store the names of the accidentals found in the notes
    accidentals_found = set()

    # Iterate over each note in the list
    for note in notes:
        # Find the pitch element in the note
        pitch = note.find(".//pitch")

        # If pitch is not found, continue to the next note
        if pitch is None:
            continue

        # Find the accidental element in the note
        accidental = note.find("accidental")

        # If accidental is not found, set accidental_text to None
        accidental_text = accidental.text if accidental is not None else None

        # If accidental_text is found in ALTER_VALUES, update the alter value
        if accidental_text in ALTER_VALUES:
            new_alter_value, _ = ALTER_VALUES.get(accidental_text)

            # Find the alter element in the pitch, if not found, create a new element
            alter_element = pitch.find("alter")
            if alter_element is None:
                alter_element = ET.SubElement(pitch, "alter")
                alter_element.tail = "\n       "

            # Set the text of the alter element to the new_alter_value
            alter_element.text = str(new_alter_value)
            accidentals_found.add(accidental_text)

    return accidentals_found


def fix_m21_parsing_makam(file_name: str, remove_alter=False) -> stream.Stream:
    """
    Fix the parsing of a Makam XML file by updating the alter values of notes,
    removing the key signature, and adding microtone deviation to pitch based on the alter value.

    Parameters:
        file_name (str): The name of the XML file to be fixed.

    Returns:
        notes (music21.stream.Stream): The stream of notes in the fixed XML file.
    """
    # Parse the XML file
    try:
        tree = ET.parse(file_name)
    except FileNotFoundError:
        print(f"File {file_name} not found")
        exit(1)

    _describe_key_signature(tree)

    # Update the alter values of notes
    notes = tree.findall(".//note")
    accidentals_found = _update_alter_values_in_xml(notes)

    print(f"Accidentals found and updated: {accidentals_found}")

    # Remove the key signature so it can be parsed by music21
    for att in tree.iter("attributes"):
        if att.find("key") != None:
            att.remove(att.find("key"))

    if remove_alter:
        # Remove all alter values from pitch
        for note in tree.findall(".//note"):
            pitch = note.find(".//pitch")
            if pitch is not None:
                alter_element = pitch.find("alter")
                if alter_element is not None:
                    pitch.remove(alter_element)

    # Save the fixed XML file with a new name
    new_file_name = file_name.replace(".xml", "_fixed_alter.xml")
    tree.write(new_file_name)

    # Parse the fixed XML score with music21
    score = converter.parse(new_file_name)

    # Convert the notes to a stream
    notes = score.flatten().notes.stream()

    # Assign microtone deviation in cents based on alter value
    for n in notes:
        if n.pitch.accidental is not None:
            alter_v, alter_default = ALTER_VALUES.get(n.pitch.accidental.name)
            if alter_v == None:
                print(n.pitch.accidental.name)
                print(alter_v)
            n.pitch.microtone = round(alter_v * TONE_DIVISION)


    return notes
