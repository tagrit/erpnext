import frappe

def execute():
    try:
        doc_type = 'Appointment Letter Template'
        
        field_name = 'introduction'
        
        meta = frappe.get_meta(doc_type)
        
        if field_name in [field.fieldname for field in meta.fields]:
            for field in meta.fields:
                if field.fieldname == field_name:
                    field.fieldtype = 'Text Editor'
                    field.save()
                    break
        else:
            print(f"Field '{field_name}' not found in '{doc_type}' DocType.")
    
    except Exception as e:
        print(f"Error: {e}")