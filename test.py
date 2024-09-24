excel_file_count = 0
    # Create an excel file
    excel_file = f"prep_and_checklists/Order_list_{event_name}/{event_name}_{current_date}_{excel_file_count}.xlsx"
    # Continously checks until it finds a non-existent file name
    while os.path.exists(excel_file):
        excel_file_count += 1
        # This updates the file_count, allowing for it to be checked again in the while loop
        excel_file = f"prep_and_checklists/Order_list_{event_name}/{event_name}_{current_date}_{excel_file_count}.xlsx"
    
    #print(excel_file)
    # Function to format the headers and add borders
    def format_headers_and_borders(sheet, start_row, start_col, end_col):
        thin_border = Border(left=Side(style='thin'),
                            right=Side(style='thin'),
                            top=Side(style='thin'),
                            bottom=Side(style='thin'))
        
        # Define the font for non-header cells
        cell_font = Font(name="Arial", size=12)

        # Define the alignment for all cells
        cell_alignment = Alignment(horizontal='center', vertical='center')

        
        # Apply font to the entire table
        for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=start_col, max_col=end_col):
             for cell in row:
                cell.font = cell_font
                # Center all data
                cell.alignment = cell_alignment
        # Format headers
        for cell in sheet.iter_cols(min_row=start_row, max_row=start_row, min_col=start_col, max_col=end_col):
            for c in cell:
                c.font = Font(bold=True, name='Calibri', size=14, color="000000")
                c.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
                c.border = thin_border

        # Apply borders to the entire table
        for row in sheet.iter_rows(min_row=start_row, max_row=sheet.max_row, min_col=start_col, max_col=end_col):      
            for cell in row:
                cell.border = thin_border
               
                
    # Function to set print options
    def set_print_options(sheet):
        sheet.print_options.gridLines = False
        sheet.page_setup.orientation = 'portrait'
    
    # Function to insert unformatted rows
    def insert_blank_rows(sheet, start_row):
        sheet.insert_rows(start_row, 1)


    # Creates an unfinished excel file
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        current_row = 3
        for ingredient in to_order:
            to_order.to_excel(writer, sheet_name= event_name, startrow=current_row, startcol=0)

    # Load the workbook and access the sheet
    workbook = load_workbook(excel_file)
    sheet = workbook[event_name]

    
    # Insert Event Info
    title = sheet.cell(row=1, column=1, value=f"{event_name} {event_date}")
    title.font = Font(name='Calibri', size=16, bold=True, underline='single', color='000000')
   
    # Set print options
    set_print_options(sheet)

    # Save the workbook with formatting
    workbook.save(excel_file)