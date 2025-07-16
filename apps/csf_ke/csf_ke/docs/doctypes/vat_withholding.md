# Feature: Importing Customer VAT Withholding from KRA to ERPNext

## 1. Purpose

This doctype allows users to import VAT Withholding data directly from the Kenya Revenue Authority (KRA)/iTax website into ERPNext using the built-in Data Import tool. The goal is to simplify tax reconciliation, ensure compliance, and automate financial entries.

## 2. Workflow Overview

1.  **Download VAT Withholding Data from iTax**
    * Users log in to the iTax portal and export their VAT Withholding Certificate as a Excel file.
2.  **Use ERPNext’s Data Import Tool**
    * Navigate to Data Import in ERPNext.
    * Select the VAT Withholding Doctype.
    * Upload the exported Excel file or attach a google sheets link to a google sheet that is publicly available.
    * Map columns to match ERPNext fields (if necessary).
    * Import the data.
3.  **VAT Withholding Doctype Entry**
    * Each imported record is stored as a new VAT Withholding document.
    * Users can review entries before submission.
4.  **Automated Journal Entry Creation (Upon Submission)**
    * When a VAT Withholding record is submitted:
        * A Journal Entry is automatically created.
        * The withholding amount is credited to the predefined Withholding VAT Payable account.
        * The corresponding customer account is debited accordingly.
        * The Journal Entry is linked to the VAT Withholding record for easy tracking.

## 3. Key Implementation Details

* **Company Doctype Enhancements**
    * Added default Withholding VAT Payable Account to ensure correct financial postings.
* **VAT Withholding Doctype**
    * Created a new submittable Doctype to track customer VAT Withholding transactions.
    * Includes fields for:
        * Customer Name
        * KRA PIN
        * Withheld Amount
        * Date of Transaction
        * Journal Entry Link
* **Custom Script for Journal Entry Automation**
    * Implemented an `on_submit` trigger to create a Journal Entry automatically.
    * Journal Entry follows the correct debit/credit mapping based on the Company’s default accounts.
    * Ensures compliance with tax reporting by maintaining accurate records.

## 4. Screenshots & UI Changes

* **Company Default VAT Withholding Accounts**

![VAT Withholding](../images/doctypes/vat_withholding_default_accounts.png)

* **Data Import Tool Interface for VAT Withholding**

![Data Import](../images/doctypes/vat_withholding_import.png)

* **VAT Withholding Doctype Example**

![VAT Withholding](../images/doctypes/vat_withholding.png)

* **Journal Entry Automation**

![VAT Withholding](../images/doctypes/journal_entry.png)

## 5. Benefits & Impact

* ✅ **Automates tax compliance** – Reduces manual effort in recording withheld VAT.
* ✅ **Improves accuracy** – Eliminates errors from manual bookkeeping.
* ✅ **Enhances traceability** – Links VAT Withholding records with Journal Entries.
* ✅ **Streamlines reconciliation** – Helps finance teams match iTax records with ERPNext.