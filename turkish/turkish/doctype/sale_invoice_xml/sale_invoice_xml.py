# -*- coding: utf-8 -*-
# Copyright (c) 2021, usama and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re
import xml.etree.ElementTree as ET

class SaleInvoiceXML(Document):
	pass

@frappe.whitelist(allow_guest=True)
def parse_xml(xml_file):
	#print(xml_file)
	arr = re.split('/',xml_file);
	path = frappe.get_site_path(arr[1],arr[2],arr[3]);
	#print(path)
	root = ET.parse(path).getroot()
	#print(root)
	filter_data = {}
	invoice_line_data = []
	invoice_data = {}
	invoice_kdv_data = {}
	final_kdv_data = []
	for invLine in root.findall("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceLine"):
		for detail in invLine:
			if detail.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity":
				quantity = detail.text
				filter_data['quantity'] = quantity
			if detail.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount":
				amount = detail.text
				filter_data['amount'] = amount	
			if detail.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal":
				for tax in detail:
					for subtax in tax:
						if subtax.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount":
							kdv_amount = subtax.text
							filter_data['kdv_amount'] = kdv_amount
						if subtax.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent":
							percentage = subtax.text
							filter_data['percentage'] = percentage		
						for taxcategory in subtax:
							for taxscheme in taxcategory:
								if taxscheme.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name":
									scheme_name = taxscheme.text
									filter_data['scheme_name'] = scheme_name	
			if detail.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item":
				for item in detail:
					if item.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name":
						item_name = item.text
						filter_data['item_name'] = item_name
			if detail.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price":
				for price in detail:
					if price.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount":
						price = price.text
						filter_data['price'] = price
		filter_data_copy = filter_data.copy()
		invoice_line_data.append(filter_data_copy)			
	#print(invoice_line_data)

	for first in root:
		if first.tag == "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID":
			invoice_no = first.text
			invoice_data['invoice_no'] = invoice_no
		if first.tag == "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate":
			invoice_date = first.text
			invoice_data['invoice_date'] = invoice_date
		for second in first:
			if second.tag == "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PaymentDueDate":
				expiry_date = second.text
				invoice_data['expiry_date'] = expiry_date
			if second.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TargetCurrencyCode":
				from_currency= second.text
				invoice_data['from_currency'] = from_currency
			if second.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}SourceCurrencyCode":
				to_currency= second.text
				invoice_data['to_currency'] = to_currency
			if second.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CalculationRate":
				rate = second.text
				invoice_data['calculation_rate'] = rate	
			if second.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExclusiveAmount":
				total = second.text
				invoice_data['sub_total']= total	
			if second.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PayableAmount":
				grand_total= second.text
				invoice_data['grand_total'] = grand_total	

	for supplier in root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingSupplierParty"):
		for party in supplier:
			for party_name in party:
				if party_name.tag == "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name":
					vendor_name = party_name.text
					invoice_data['vendor_name'] = vendor_name

	for customer in root.find("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingCustomerParty"):
		for party in customer:
			for party_name in party:
				if party_name.tag == "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name":
					customer_name = party_name.text
					invoice_data['customer_name'] = customer_name			
	#print(invoice_data)

	for total in root.findall("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal"):
		for subtotal in total.findall("{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal"):
			for sub in subtotal:
				if sub.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount":
					kdv=sub.text
					invoice_kdv_data['kdvA'] = kdv
				if sub.tag=="{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent":
					kdvper=sub.text
					invoice_kdv_data['kdvper']= kdvper	
			invoice_kdv_data_copy = invoice_kdv_data.copy()
			final_kdv_data.append(invoice_kdv_data_copy)
	#print(final_kdv_data)

	return invoice_line_data, invoice_data, final_kdv_data