# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes import _

def execute(filters=None):
	columns = get_columns()
	sl_entries = get_stock_ledger_entries(filters)
	item_details = get_item_details(filters)
	
	data = []
	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		voucher_link_icon = """<a href="%s"><i class="icon icon-share" 
			style="cursor: pointer;"></i></a>""" \
			% ("/".join(["#Form", sle.voucher_type, sle.voucher_no]),)
			
		data.append([sle.date, sle.item_code, item_detail.item_name, item_detail.item_group, 
			item_detail.brand, item_detail.description, sle.warehouse, item_detail.stock_uom, 
			sle.actual_qty, sle.qty_after_transaction, sle.stock_value, sle.voucher_type, 
			sle.voucher_no, voucher_link_icon, sle.batch_no, sle.serial_no, sle.company])
	
	return columns, data
	
def get_columns():
	return ["Date:Datetime:95", "Item:Link/Item:100", "Item Name::100", 
		"Item Group:Link/Item Group:100", "Brand:Link/Brand:100",
		"Description::200", "Warehouse:Link/Warehouse:100",
		"Stock UOM:Link/UOM:100", "Qty:Float:50", "Balance Qty:Float:80", 
		"Balance Value:Currency:100", "Voucher Type::100", "Voucher #::100", "Link::30", 
		"Batch:Link/Batch:100", "Serial #:Link/Serial No:100", "Company:Link/Company:100"]
	
def get_stock_ledger_entries(filters):
	if not filters.get("company"):
		webnotes.throw(_("Company is mandatory"))
	if not filters.get("from_date"):
		webnotes.throw(_("From Date is mandatory"))
	if not filters.get("to_date"):
		webnotes.throw(_("To Date is mandatory"))
		
	return webnotes.conn.sql("""select concat_ws(" ", posting_date, posting_time) as date,
			item_code, warehouse, actual_qty, qty_after_transaction, 
			stock_value, voucher_type, voucher_no, batch_no, serial_no, company
		from `tabStock Ledger Entry`
		where company = %(company)s and
			posting_date between %(from_date)s and %(to_date)s
			{sle_conditions}
			order by posting_date desc, posting_time desc, name desc"""\
		.format(sle_conditions=get_sle_conditions(filters)), filters, as_dict=1)

def get_item_details(filters):
	item_details = {}
	for item in webnotes.conn.sql("""select name, item_name, description, item_group, 
			brand, stock_uom from `tabItem` {item_conditions}"""\
			.format(item_conditions=get_item_conditions(filters)), filters, as_dict=1):
		item_details.setdefault(item.name, item)
		
	return item_details
	
def get_item_conditions(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("name=%(item_code)s")
	if filters.get("brand"):
		conditions.append("brand=%(brand)s")
	
	return "where {}".format(" and ".join(conditions)) if conditions else ""
	
def get_sle_conditions(filters):
	conditions = []
	if filters.get("warehouse"):
		conditions.append("warehouse=%(warehouse)s")
	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")
	
	return "and {}".format(" and ".join(conditions)) if conditions else ""