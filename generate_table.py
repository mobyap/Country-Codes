import os
import sys

from icc.core import list_all_countries, get_special_codes, get_app_codes_list

def generate_markdown():
    countries = list_all_countries()
    specials = get_special_codes()
    apps = get_app_codes_list()

    with open('table.md', 'w') as f:
        f.write('# ICC Codes Tables\n\n')
        
        f.write('## Country Codes\n\n')
        f.write('| Rank | Country | Official Name | ISO-2 | ISO-3 | ICC Code | Land Area (km²) | Phone Code |\n')
        f.write('|------|---------|---------------|-------|-------|----------|-----------------|------------|\n')
        for c in countries:
            f.write(f'| {c["rank"]} | {c["name"]} | {c["official_name"]} | {c["iso_alpha2"]} | {c["iso_alpha3"]} | {c["icc_code"]} | {c["land_area_km2"]:,} | {c["phone_code"]} |\n')

        f.write('\n## Special Codes (Reserved)\n\n')
        f.write('| Code | Purpose | Category |\n')
        f.write('|------|---------|----------|\n')
        for s in specials:
            f.write(f'| {s["formatted"]} | {s["purpose"]} | {s["category"]} |\n')

        f.write('\n## Mobyap App Codes\n\n')
        f.write('| Code | Purpose |\n')
        f.write('|------|---------|\n')
        for a in apps:
            f.write(f'| {a["formatted"]} | {a["purpose"]} |\n')

if __name__ == "__main__":
    generate_markdown()
    print("table.md generated successfully.")
