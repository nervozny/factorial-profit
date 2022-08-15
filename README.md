# Factorial Profit Analysis

This is a project of interactive factorial profit analysis toolkit desinged for Marketing and Sales departments.  

Please check out the demo app made with Streamlit web platform  https://nervozny-factorial-profit-app-ixvnah.streamlitapp.com/ 

Originally it was designed with Dash Plotly framework, the code is also available in the repo.  

This is a real project that was implemented in a company I worked for, however, due to the non-disclosure agreement all names and data have been changed. Also, for demonstration purposes, the date range is limited to the period from March to December 2020.


## Theory
The chain substitution method that is used in this project is a classiс method that allows you to determine the independent influence of each of the components (factors) on the delta profit. The approach to extracting factors is as follows: you successively substitute the factors of the base time interval with the factors of the actual (fact) period. The factors I use for profit analysis in this project are price, cost and quantity (structure) of sales:

If Profit = Quantity $\times$ (Price - Cost),
so the chain substitution would look like this:

Price influence = Quantity<sub>fact</sub>  $\times$ (Price<sub>fact</sub> - Price<sub>base</sub>)  
Cost influence = Quantity<sub>fact</sub>  $\times$ (Cost<sub>base</sub> - Cost<sub>fact</sub>)  
Volume influence = (Quantity<sub>fact</sub> - Quantity<sub>base</sub>)  $\times$ (Price<sub>base</sub> - Cost<sub>base</sub>)

## Practice
Since it's a marketing and sales analysis instrument, we not only want to be able to tell which of the three factors influenced the profit difference, but at the same time we want to understand how each product or client (or higher level hierarchies like brand or branch) contributes to the resulting difference. If your company sells just one type of product and has only one client, the solution is pretty straitforward. It is also simple if you have many products and only one client (or vice versa). However, in real world the range of products and the number of clients is usually in the thousands and after you have answered the question, for example, which product most of all contributed to the drop in profit due to price factor, you most likely would like to know which customer bought this product at such a low price. Answering both questions at once is a bit more tricky.  
What I came up with is to use the combination of product and client as a lower level of granularity.
![image](https://user-images.githubusercontent.com/102557512/184645631-26b8da39-3101-4a96-a256-e0588832ebd2.png)  
The back side of this approach is that the size of your dataframe increases dramatically.

