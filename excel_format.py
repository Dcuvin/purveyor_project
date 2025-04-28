
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation


def format_headers_and_borders(sheet, start_row, start_col, end_col):
    thin_border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
        
    # Define the font for non-header cells
    cell_font = Font(name="Calibri", size=14)

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
        # Set print settings to fit on one page
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 1  # 0 means "as many as needed"
    
# Function to insert unformatted rows
def insert_blank_rows(sheet, start_row):
    sheet.insert_rows(start_row, 1)
