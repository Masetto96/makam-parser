import xml.etree.ElementTree as ET

altervalues = {
    "flat": -9,
    "sharp": +9,
    "quarter-flat": -4,
    "quarter-sharp": +4,
    "slash-flat": -5,
    "slash-quarter-sharp": +5,
    "double-slash-flat": -8,
    "slash-sharp": +8,
}

FILE_NAME = "hicaz--sarki--aksaksemai--sezdim_dargin--rifat_ayaydin.xml"

if __name__ == "__main__":
    # Load the MusicXML file
    try:
        tree = ET.parse(FILE_NAME)
    except FileNotFoundError:
        print(f"File {FILE_NAME} not found")
        exit(1)

    # Find all the 'note' elements in the XML tree
    notes = tree.findall(".//note")

    # Keep track of the accidentals found
    accidentals_found = set()

    for c, note in enumerate(notes, start=1):
        # Find the 'pitch' element of the current note
        pitch = note.find(".//pitch")
        # If there's no pitch, it's a rest (no pitch == rest)
        if pitch is None:
            continue

        accidental = note.find("accidental")
        # If there's no accidental, assign None to accidental_text
        accidental_text = accidental.text if accidental is not None else None

        # If the accidental is defined in altervalues, update the alter value
        if accidental_text in altervalues:
            new_alter_value = altervalues[accidental_text]
            print(f"Updating {accidental_text} to {new_alter_value} in {c}th note")

            alter_element = pitch.find("alter")
            # If there's no alter element, create a new one
            if alter_element is None:
                alter_element = ET.SubElement(pitch, "alter")
            # Set the new alter value
            alter_element.text = str(new_alter_value)

            accidentals_found.add(accidental_text)

    print(f"Accidentals found {accidentals_found}")
    tree.write("test420.xml")
