import csv
import html
import os


def process_input_data(input_filename='kpd_classification_hr.csv'):
    """
        Reads the source CSV and processes it into a structured list of records,
        correctly handling hierarchical codes with significant trailing zeros.
    """
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' not found.")
        return None

    print(f"Reading and processing '{input_filename}'...")

    processed_records = []
    # Map to find a parent's external ID using its code
    code_to_external_id_map = {}
    # Map to find a parent's code using its level (the new, improved logic)
    last_seen_code_at_level = {}

    with open(input_filename, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=',')

        for i, row in enumerate(reader):
            if not row or len(row) < 2:
                continue

            code = row[0].strip()
            name_hr = row[1].strip()
            name = row[2].strip()
            date_start = row[3].strip()

            if 'code' in code or 'KPD' in code or not code:
                continue

            # --- New, more robust hierarchy logic ---
            level = 0
            parent_code = None
            parts = code.split('.')

            # 1. Determine the level of the current code
            if len(parts) == 1:
                if len(code) == 1 and code.isalpha():
                    level = 1
                elif len(code) == 2 and code.isdigit():
                    level = 2
            elif len(parts) == 2:
                level = 3 if len(parts[1]) == 1 else 4
            elif len(parts) == 3:
                level = 5 if len(parts[2]) == 1 else 6

            if level == 0:
                print(f"Warning: Could not determine level for code '{code}'. Skipping row {i + 1}.")
                continue

            # 2. Determine the parent code based on the level
            parent_level = level - 1
            if parent_level > 0:
                parent_code = last_seen_code_at_level.get(parent_level)

            # 3. Update the tracking map for the current level
            last_seen_code_at_level[level] = code

            # --- Generate Odoo-compatible IDs ---
            external_id = f"l10n_hr_kpd.{code.replace('.', '_')}"
            parent_external_id = code_to_external_id_map.get(parent_code)

            processed_records.append({
                'id': external_id,
                'code': code,
                'name': name,
                'name_hr': name_hr,
                'date_start': date_start,
                'level': level,
                'parent_id/id': parent_external_id or ""
            })

            # Store the current record's ID so its children can find it
            code_to_external_id_map[code] = external_id

    return processed_records


def generate_csv_file(records, output_filename='l10n_hr_kpd_data.csv'):
    """
        Writes the processed records to a CSV file.
    """
    with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['id', 'code', 'name', 'date_start', 'level', 'parent_id/id'])
        writer.writeheader()
        writer.writerows(records)
    print(f"\nSuccessfully created CSV file: '{output_filename}'")


def generate_xml_file(records, output_filename='l10n_hr_kpd_data.xml'):
    """Writes the processed records to an Odoo XML file."""
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('<?xml version="1.0" encoding="utf-8"?>\n')
        outfile.write('<odoo>\n')
        outfile.write('    <data noupdate="1">\n\n')

        for record in records:
            safe_name = html.escape(record['name'])

            outfile.write(f'        <record id="{record["id"]}" model="l10n.hr.kpd">\n')
            outfile.write(f'            <field name="code">{record["code"]}</field>\n')
            outfile.write(f'            <field name="name">{safe_name}</field>\n')
            outfile.write(f'            <field name="date_start">{record["date_start"]}</field>\n')
            outfile.write(f'            <field name="level">{record["level"]}</field>\n')

            if record['parent_id/id']:
                outfile.write(f'            <field name="parent_id" ref="{record["parent_id/id"]}"/>\n')

            outfile.write('        </record>\n\n')

        outfile.write('    </data>\n')
        outfile.write('</odoo>\n')
    print(f"\nSuccessfully created XML file: '{output_filename}'")


def generate_po_file(records, output_filename='l10n_hr_kpd_hr.po'):
    """Writes the processed records to an Odoo XML file."""
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.write('''# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* l10n_hr_kpd
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 18.0+e\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-11-11 12:04+0000\\n"
"PO-Revision-Date: 2025-11-11 12:04+0000\\n"
"Last-Translator: \\n"
"Language-Team: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: \\n"
"Plural-Forms: \\n''')
        for record in records:
            safe_name = html.escape(record['name'])
            safe_name_hr = html.escape(record['name_hr'])
            outfile.write("""
#. module: l10n_hr_kpd
#: model:l10n.hr.kpd,name:{id}
msgid "{name}"
msgstr "{name_hr}"
            """.format(id=record['id'], name=safe_name, name_hr=safe_name_hr))
    print(f"\nSuccessfully created PO file: '{output_filename}'")


if __name__ == "__main__":
    # Get user's choice for the output format
    choice = ''
    while choice not in ['csv', 'xml', 'po']:
        choice = input("Choose the output format (csv or xml or po): ").lower().strip()
        if choice not in ['csv', 'xml', 'po']:
            print("Invalid choice. Please type 'csv', 'xml' or 'po'.")

    # Process the data from the input file
    processed_data = process_input_data()

    if processed_data:
        # Generate the file based on user's choice
        if choice == 'csv':
            generate_csv_file(processed_data)
        elif choice == 'xml':
            generate_xml_file(processed_data)
        elif choice == 'po':
            generate_po_file(processed_data)
