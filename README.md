# Factorial Profit Analysis

This is a project of interactive factorial profit analysis toolkit desinged for Marketing and Sales departments.  

Please check out the demo app made with Streamlit web platform  https://nervozny-factorial-profit-app-ixvnah.streamlitapp.com/ 

Originally it was designed with Dash Plotly framework, the code is also available in the repo.  

This is a real project that was implemented in a company I worked for, however, due to the non-disclosure agreement all names and data have been changed. Also, for demonstration purposes, the date range is limited to the period from March to December 2020.


## Theory

The chain substitution method that is used in this project is a classiс method that allows you to determine the independent influence of each of the components (factors) on the delta profit. The approach to extracting factors is as follows: you successively substitute the factors of the base time interval with the factors of the actual (fact) time interval. The factors I use for profit analysis in this project are price, cost and quantity (structure) of sales.

If Profit = Quantity $\times$ (Price - Cost),
so the chain substitution would look like this:

Price influence = Quantity<sub>fact</sub>  $\times$ (Price<sub>fact</sub> - Cost<sub>base</sub>)  
Cost influence = Quantity<sub>fact</sub>  $\times$ (Price<sub>base</sub> - Cost<sub>fact</sub>)  
Quantity influence = (Quantity<sub>fact</sub> - Quantity<sub>base</sub>)  $\times$ (Price<sub>base</sub> - Cost<sub>base</sub>)

## Practice

Since it's a marketing and sales analysis instrument, we not only want to be able to tell which of the three factors influenced the profit difference, but at the same time we want to understand how each product or client (or higher level hierarchies like brand or branch) contributes to the resulting difference. If your company sells just one type of product and has only one client, the solution is pretty straightforward. It is also simple if you have many products and only one client (or vice versa). However, in real world the range of products and the number of clients is usually in the thousands and after you have answered the question, for example, which product most of all contributed to the drop in profit due to price factor, you most likely would like to know which customer bought this product at such a low price. Answering both questions at once is a bit more tricky.  
What I came up with is to use the combination of product and client as a lower level of granularity.
The back side of this approach is that the size of your dataframe increases dramatically.

## Example of use

Three heatmaps and a set of filters allow you to visually evaluate the most important changes in profit.  
For example we can see there was an overall decrease of 204.8k in profit in autumn compared to summer 2020.
Also, we note that there is a drop in profit of 25.6K for the KAR brand in branch Derry due to the price factor with no compensation in cost or structure:  

![image](https://user-images.githubusercontent.com/102557512/184663709-64c3cd02-6e63-4d69-9573-6a0b3b495fcf.png)

As a Head of Marketing we might want to drill down and find out what group of products in which sales channels were affected. To do this we fix brand KAR and branch Derry in the filter section and place product group and sales channel on the axes:      

![image](https://user-images.githubusercontent.com/102557512/184666526-73cdffb5-909d-4617-9a27-3faa89fa6c9c.png)

In the fall something happened to Witch Jelly (KAR brand) products in the Derry branch when selling through the DIY channel.

As a KAR Brand Manager, Witch Jelly Product Manager or Derry Sales Manager we probably would like to drill even further and take a look at the exact products and clients responsible for this. To go down to the lowest level there is an export section which allows to export the required slice of data to MS Excel and provides all the calculations and raw data.

![image](https://user-images.githubusercontent.com/102557512/184673302-ed847a21-898e-4a2d-ae66-f5e29ba2def3.png)

This information answers our initial quiestion (drop in profit of 25.6K for the KAR brand in branch Derry): obviously there was one client (id 155215) who purchased a lot of KAR products (Witch Jelly and Batteries mostly) and probably asked for a considerable discount. Sometimes this tradeoff was justified by the increase of profit due to the number of pieces sold, sometimes not. In any case the Sales Manager in Derry has some homework to do.


## Dash Plotly
The Dash implementation works similarly but the design is slightly different:

![image](https://user-images.githubusercontent.com/102557512/184679530-39f9d8c3-9541-40b0-b566-884452cbb14f.png)

