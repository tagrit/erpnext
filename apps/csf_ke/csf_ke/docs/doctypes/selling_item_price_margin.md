# Selling Item Price Margin 

The **Selling Item Price Margin** doctype enhances the functionality of setting and updating item prices based on profit margins derived from specific price lists and cost metrics. This document outlines the functionality and setup required to use this script effectively.

## Features

- **Custom Profit Margins**: Users can specify a profit margin based on either the valuation rate or the buying price of items.
- **Flexible Profit Types**: Choose to add a profit margin as a fixed amount or a percentage.
- **Price List Selection**: Users Select Buying price lists to calculate the desired selling price.
- **Automatic Price List Creation**: For items not previously listed, the script will create a new item price list entry of type selling with the calculated price or update the rate of the already existing price list.

## Workflow

1. **Set the Duration Period**: That is the duration for when the Selling Item Price Margin Rule will take effect. E.g., Start Date: 01-01-2024 to End Date: 31-12-2024

![image](https://github.com/user-attachments/assets/c3531ffb-2083-4a22-a856-b441f5b60a59)

2. **Set the Price List Action**:  Whether you want new Item Prices to be created or to update the already existing Item Prices.

![image](https://github.com/user-attachments/assets/9e5ef4b7-b24b-4d88-98f4-27e309becbbf)

3. **Select Selling Price List**: Start by choosing a Selling Price from price list from which you want to derive profit margins.

![image](https://github.com/user-attachments/assets/38fca4e4-a303-46d8-b01e-55773c6bbf71)

4. **Select Buying Price List for the Profit Margin Basis**:

![image](https://github.com/user-attachments/assets/b5c68dd1-924c-41ce-afe7-e1c0eca11428)

5. **Define Profit Margin**: Price Margin Value Section

   - Specify the profit margin type (Amount or Percentage).
   
![image](https://github.com/user-attachments/assets/3fb85661-5edb-4c02-ad3e-3758f426cfdb)

   - Enter the value of the profit margin.

![image](https://github.com/user-attachments/assets/dfc8df28-6a28-4950-bf9f-a0793281ca24)

6. **Specify the Items Margin Should be Applied To**: In the Items child table you can specify the Items for which you want the Profit to be assigned. N/B: An Item cannot be in two Documents with active start and end date.

![image](https://github.com/user-attachments/assets/687c4aeb-6520-4d6d-b43a-8a393d2b976c)

7. **Execution**:

   - Upon submission of a purchase receipt or purchase invoice (N/B with update_stock being true), the script calculates the new item selling price by adding the specified profit margin to the item's base cost.

