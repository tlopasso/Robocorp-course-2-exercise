from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robots_from_RobotSpareBins():
    """"Second course of Robocorp certification"""
    browser =open_website()
    table_content=download_read_csv()
    loop_orders(browser,table_content)


def open_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page=browser.page()
    page.click("button:text('OK')")
    return browser


def download_read_csv():
    http=HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)


    #leggo il csv in una tabella
    tables=Tables()
    table_content=tables.read_table_from_csv("orders.csv")
    return table_content

def loop_orders(browser, table):
    #inseririsco a loop tutti gli ordini del csv
    page=browser.page()
    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    for row in table:
        head_number = row["Head"]
        page.select_option("#head", head_names.get(head_number))
        page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(row["Body"]))
        page.fill("input[placeholder='Enter the part number for the legs']", row["Legs"])
        page.fill("#address", row["Address"])
        while True:
            page.click("#order")
            order_another = page.query_selector("#order-another")
            if order_another:
                save_order(row["Order number"])
                page.click("#order-another")
                page.click('text=OK')
                break

def save_order(order_number):
    pdf = store_receipt_as_pdf(order_number)
    screen = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screen, pdf)
    archive_receipts()
    clean_up()

def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path 

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path=pdf_file, output_path=pdf_file)

def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():
    """Cleans up the folders where receipts and screenshots are saved."""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")