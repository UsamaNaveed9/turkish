// Copyright (c) 2021, usama and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sale Invoice XML', {
	// refresh: function(frm) {

	// }
	file:function(frm){
		cur_frm.clear_table("invoice_line");
		cur_frm.refresh_fields();
		if(frm.doc.file){
			//let full_path = frappe.get_site_path('private', 'files', frm.doc.file);
			console.log(frm.doc.file)
			frappe.msgprint({
				title: __('File Upload Successfully.'),
				indicator: 'green',
				message: __('Now, You can click on the proceed button.')
			});			
		}
	},
	process_file:function(frm){
		cur_frm.clear_table("invoice_line");
		cur_frm.refresh_fields();
		let xml_file = frm.doc.file;
		if(frm.doc.file){
			frappe.call({
				method: "turkish.turkish.doctype.purchase_invoice_xml.purchase_invoice_xml.parse_xml",
				args: {
					'xml_file': xml_file
				},
				callback: function (r) {
					var info = r.message;
                    //console.log(info[0],info[1],info[2])
					var len = info[0].length;
					var symbol = info[1].symbol;
					frm.set_value('vendor_name',info[1].vendor_name)
					frm.set_value('customer_name',info[1].customer_name)
					frm.set_value('invoice_no',info[1].invoice_no)
					frm.set_value('invoice_date',info[1].invoice_date)
					frm.set_value('expiry_date',info[1].expiry_date)
					frm.set_value('from_currency',info[1].from_currency)
					frm.set_value('to_currency',info[1].to_currency)
					frm.set_value('calculation_rate',info[1].calculation_rate)
					frm.set_value('symbol',info[1].symbol)
					for (let index = 0; index < len; index++) {
						let element = info[0][index];
						//console.log(element)
						var child = cur_frm.add_child("invoice_line");
					 	frappe.model.set_value(child.doctype, child.name, "item_name", element.item_name)
					 	frappe.model.set_value(child.doctype, child.name, "quantity", element.quantity)
					 	frappe.model.set_value(child.doctype, child.name, "unit_price", symbol.concat(" ",parseFloat(element.price)))
					 	frappe.model.set_value(child.doctype, child.name, "kdv_percentage", element.percentage)
					 	frappe.model.set_value(child.doctype, child.name, "kdv_amount", symbol.concat(" ",parseFloat(element.kdv_amount)))
					 	frappe.model.set_value(child.doctype, child.name, "amount", symbol.concat(" ",parseFloat(element.amount)))
					 	cur_frm.refresh_field("invoice_line")							
					}
					frm.set_value('sub_total',symbol.concat(" ",info[1].sub_total))
					frm.set_value('grand_total',symbol.concat(" ", info[1].grand_total))
					frm.set_value('kdv_percentage',info[2][0].kdvper)
					frm.set_value('kdv_amount',symbol.concat(" ", info[2][0].kdvA))
					frm.set_value('kdv_per',info[2][1].kdvper)
					frm.set_value('kdv_a',symbol.concat(" ", info[2][1].kdvA))
				}
			})
			
		}
    }
});
