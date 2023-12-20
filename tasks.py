from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import time

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=200,
    )
    open_robot_order_website()
    orders = get_orders()
    # fill_the_form('test')
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        pdf_path = store_receipt_as_pdf(order['Order number'])
        screenshot_path = screenshot_robot(order['Order number'])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        click_order_another()
    archive_receipts('output//receipts', 'output//receipts.zip')


def open_robot_order_website():
    """Navigate to URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """Download the orders file, read it as a table, and return the result"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    return library.read_table_from_csv("orders.csv")


def close_annoying_modal():
    """Closes the popup"""
    page = browser.page()
    page.click("text=OK")


def fill_the_form(order_row):
    """Enters the order into the web page"""
    page = browser.page()
    
    page.select_option('#head', str(order_row['Head']))
    page.click(f'//*[@id="id-body-{str(order_row["Body"])}"]')
    page.fill('//input[@placeholder="Enter the part number for the legs"]', str(order_row['Legs']))
    page.fill('#address', order_row['Address'])
    page.click('#preview')    
    page.click('#order')
    

    for _ in range(5):
        time.sleep(0.1)
        if page.is_visible('.alert-danger'):
            page.click("#order")
    

def store_receipt_as_pdf(order_number):
    """Store the receipt as a PDF file and return the file path"""
    pdf = PDF()
    output_file = f'output//receipts//{order_number}.pdf'
    empty_html_content = "<html><body></body></html>"
    pdf.html_to_pdf(empty_html_content, output_file)
    return output_file


def screenshot_robot(order_number):
    """Take a screenshot of the receipt"""
    page = browser.page()
    filepath = f"output//screenshots//{order_number}.png"
    page.screenshot(path=filepath)
    return filepath
    
def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Add the screenshot to the PDF file"""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[f"{screenshot}:align=center"],  # You can specify alignment and other properties here
        target_document=pdf_file
    )

def click_order_another():
    """Clicks the button to order another robot"""
    page = browser.page()
    page.click('#order-another')


def archive_receipts(source_directory, output_zip_file):
    """Create a zip file of all the receipts"""
    lib = Archive()
    # Include only PDF files in the zip
    lib.archive_folder_with_zip(source_directory, output_zip_file, include='*.pdf')

