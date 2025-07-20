# TIMs Integration into ERPNext

## Overview

This integration enhances ERPNext by incorporating Kenya's Tax Invoice Management System (TIMs) requirements. It introduces new custom fields in the Sales Invoice Doctype, a new Doctype **(TIMs HSCode)** for managing tax classification, and dynamic filtering for accurate tax mapping. Additionally, it integrates an external supplier’s <a href="https://docs.cecypo.tech/s/kb/doc/tims-parser-Nni9r8JcjX">Cecypo</a> TIMs Parser for seamless invoice processing.

## Features

### 1. Custom Fields in Sales Invoice

To comply with TIMs, the following fields have been added to the Sales Invoice Doctype:

| Field Name           | Type | Description                                   |
| :------------------- | :--- | :-------------------------------------------- |
| etr_serial_number    | Data | Unique TIMs ETR serial number                 |
| cu_invoice_date      | Date | Invoice date recorded by TIMs                 |
| etr_invoice_number   | Data | TIMs-assigned invoice number                  |
| cu_link              | URL  | Verification link for the invoice             |

### 2. New Doctype: TIMs HSCode

A new Doctype, `TIMs HSCode`, has been introduced to store tax classification details.

**Key Fields:**

* **Item Tax**: Specifies the applicable tax template.
* **Description**: Provides additional details about the HS code.

### 3. Custom Fields in Item Tax Table

The following fields have been added to the Item Tax table:

| Field Name    | Type       | Description                                  |
| :------------ | :--------- | :------------------------------------------- |
| tims_hscode   | Link       | Links to the TIMs HSCode Doctype             |
| description   | Read Only  | Auto-fetches the HSCode description          |

### 4. Dynamic Filtering

To ensure accurate selection of HS codes, the `TIMs HSCode` field in the Item Tax table is dynamically filtered based on the Item Tax Template.

**Filter Logic:**

Only HS codes that match the Item Tax Template of the current item are displayed.

## TIMs Parser Integration

We are utilizing an external TIMs Parser for processing and validating TIMs invoices. This parser handles:

* Extraction of ETR serial numbers, invoice dates, and numbers from TIMs.
* Verification and linking of TIMs invoices via `cu_link`.
* Ensuring compliance with KRA requirements.

## Setup Instructions

1.  **Configure TIMs HSCode**
    * Navigate to `TIMs HSCode`.
    * Add new HS codes with their corresponding Item Tax Template.
    * Or update the already existing HSCodes with their corresponding 
2.  **Ensure Custom Fields in Sales Invoice**
    * Go to `Sales Invoice`.
    * Ensure the four TIMs fields (`etr_serial_number`, `cu_invoice_date`, etc.) are visible in the Sales Invoice form.
3.  **Import HS Codes (Optional)**
    * Use ERPNext’s Data Import Tool to bulk upload HS codes.
4.  **Cecypo's External TIMs Parser Integration**
    <a href="https://docs.cecypo.tech/s/kb/doc/erpnext-O7U5xeE9DN">Cecypo TIMs Integration with ERPNext</a>

## Usage

### Generating a TIMs-Compliant Invoice

1.  Create a Sales Invoice.
2.  Select the appropriate Item Tax Template.
3.  Ensure the TIMs HSCode is populated for tax compliance.
4.  Upon submission, TIMs details will be fetched and linked via the external parser.

### Verifying TIMs Invoice

* Click on the `cu_link` to verify the invoice on the KRA portal.

## Benefits

* ✅ **Ensures KRA compliance** – Automates TIMs invoice generation.
* ✅ **Enhances tax accuracy** – Uses HSCode mapping for proper tax classification.
* ✅ **Simplifies reconciliation** – TIMs details are automatically linked to invoices.
* ✅ **Reduces manual effort** – External parser handles TIMs invoice extraction.

## Support

For any issues or customizations, please contact the ERPNext support team or your TIMs Parser provider.

## Future Enhancements

* Automated reconciliation of TIMs data with ERPNext financials.
* Real-time tax rate updates based on HSCode changes.
* Enhanced error handling for TIMs invoice validation.

This integration ensures seamless compliance with Kenya’s TIMs regulations while maintaining a smooth ERPNext workflow.
