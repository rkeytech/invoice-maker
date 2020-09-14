'''
-Headers: "Content-Type: application/json"
-Content: '{"from":"Invoiced, Inc.", "to":"Parag",
            "logo":"https://invoiced.com/img/logo-invoice.png",
            "number":1,
            "items":[{"name":"Starter plan","quantity":1,"unit_cost":99}],
            "notes":"Thanks for your business!"}'
'''
import typer
import requests
import os
import csv
from dataclasses import dataclass
from typing import List
import random
import string


@dataclass
class Invoice:
    from_who: str
    to_who: str
    logo: str
    number: str
    date: str
    due_date: str
    items: List[dict]
    notes: str


class CSVParser:
    def __init__(self, csv_file):
        self.field_names = (
            'from_who',
            'to_who',
            'logo',
            'number',
            'date',
            'due_date',
            'items',
            'notes'
        )
        self.csv_file = csv_file

    def get_invoices_from_csv(self):
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            header = True
            invoices = []

            for line in reader:
                if header:
                    header = False
                    continue

                invoice_item = Invoice(**line)
                invoice_item.items = eval(invoice_item.items)
                invoice_item.number = ''.join(random.choices(
                    string.digits, k=6))
                invoices.append(invoice_item)

        return invoices


class MakeInvoice:
    def __init__(self):
        self.endpoint = "https://invoice-generator.com"
        self.invoice_dir = f"{os.path.dirname(os.path.abspath(__file__))}" \
            + '/invoices'
        self.headers = {'Content-Type': 'application/json',
                        'Accept-Language': 'el-GR'}

    def convertJSON(self, invoice: Invoice):
        parsed = {
            'from': invoice.from_who,
            'to': invoice.to_who,
            'logo': invoice.logo,
            'number': invoice.number,
            'date': invoice.date,
            'due_date': invoice.due_date,
            'items': invoice.items,
            'notes': invoice.notes
        }
        return parsed

    def save_to_pdf(self, content, invoice: Invoice):
        invoice_name = f"{invoice.number}_invoice.pdf"
        invoice_path = f"{self.invoice_dir}/{invoice_name}"
        with open(invoice_path, 'wb') as f:
            typer.echo(f"Making invoice {invoice_name}")
            f.write(content)

    def get_invoice(self, invoice):
        r = requests.post(self.endpoint,
                          json=self.convertJSON(invoice),
                          headers=self.headers)

        if r.status_code == 200:
            self.save_to_pdf(r.content, invoice)
            typer.echo("File Saved!")
        else:
            typer.echo(f"Fail: {r.text}")


def main(csv_file: str = typer.Argument('invoices.csv')):
    typer.echo(f"Running script with {csv_file}")
    maker = MakeInvoice()
    parser = CSVParser(csv_file)
    invoices = parser.get_invoices_from_csv()

    for invoice in invoices:
        maker.get_invoice(invoice)


if __name__ == "__main__":
    typer.run(main)
