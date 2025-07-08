import sqlite3
from jinja2 import Environment, FileSystemLoader, select_autoescape

def update_dropdown_menu_selection(db):
    """Grab all item_name rows under canape sub_category."""
    conn = sqlite3.connect(db)
    cur  = conn.cursor()
    cur.execute(
        """SELECT item_name 
        FROM menu_items 
        WHERE sub_category = 'canape' 
        ORDER BY item_name;""",
    )
    canapes = [row[0] for row in cur.fetchall()]
    

    """Grab all item_name rows under starter category."""
    cur.execute(
        """SELECT item_name 
        FROM menu_items 
        WHERE category = 'starter' 
        ORDER BY item_name;""",
    )
    starters = [row[0] for row in cur.fetchall()]

    """Grab all item_name rows under entree category."""
    cur.execute(
        """SELECT item_name 
        FROM menu_items 
        WHERE category = 'entree' 
        ORDER BY item_name;""",
    )
    entrees = [row[0] for row in cur.fetchall()]
    conn.close()
# Render template with fetched data
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('beo_form_template.html')
    rendered_html = template.render(canapes=canapes, starters=starters, entrees=entrees)
    # Write out the updated HTML
    with open('beo_form_final.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"✅ BEO HTML updated: {'beo_form_final.html'}")