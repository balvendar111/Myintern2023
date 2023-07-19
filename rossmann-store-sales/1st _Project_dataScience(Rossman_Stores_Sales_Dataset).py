#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns


# In[4]:


stores_lookup = pd.read_csv('store.csv')


# In[5]:


sales_data = pd.read_csv('train.csv', low_memory=False)


# In[6]:


stores_lookup.head()


# In[7]:


stores_lookup.shape


# In[8]:


stores_lookup.info()


# In[9]:


sales_data.head(10)


# In[10]:


sales_data.info()


# In[11]:


print(sales_data["Date"].min())
print(sales_data["Date"].max())


# In[12]:


merged_sales = sales_data.merge(stores_lookup, how='left', on="Store", validate="many_to_one")


# In[13]:


merged_sales


# In[14]:


merged_sales.describe()


# In[15]:


merged_sales[["DayOfWeek", 'Sales', 'Customers', 'CompetitionDistance']].skew()


# In[16]:


merged_sales[["DayOfWeek", 'Sales', 'Customers', 'CompetitionDistance']].kurtosis()


# In[17]:


fig, axes = plt.subplots(nrows=1, ncols=2)

merged_sales.hist(column='Sales', bins='sturges', ax=axes[0])
merged_sales.hist(column='Customers', bins='sturges', ax=axes[1])

fig.set_size_inches(15, 5)
plt.show()  


# In[18]:


print("skew     " + str(round(merged_sales['Sales'].skew(),6)))
print("kurtosis " + str(round(merged_sales['Sales'].kurtosis(),6)))
print(merged_sales['Sales'].describe().round(3))
print("mode     " + str(merged_sales['Sales'].mode()))


# In[19]:


merged_sales['Date'] = pd.to_datetime(merged_sales['Date'], format="%Y-%m-%d", errors='raise')


# In[20]:


merged_sales.info()


# In[21]:


merged_sales["Year"] = merged_sales["Date"].dt.year
merged_sales["Month"] = merged_sales["Date"].dt.month
merged_sales["DayOfMonth"] = merged_sales["Date"].dt.day


# In[22]:


print("Rows before dropping duplicates: " + str(merged_sales.shape[0]))
merged_sales = merged_sales.drop_duplicates()
print("Rows after dropping duplicates: " + str(merged_sales.shape[0]))


# In[23]:


for col in merged_sales:
    if merged_sales[col].dtype == object:
        merged_sales[col] = merged_sales[col].str.strip()


# In[24]:


for col in merged_sales:
    if merged_sales[col].dtype == object:
        print(merged_sales[col].value_counts())


# In[25]:


check_cols = [ 'Open', 'Promo', 'Promo2', 'SchoolHoliday',  'DayOfWeek', 'CompetitionOpenSinceMonth',  'CompetitionOpenSinceYear', 'Promo2SinceWeek', 'Promo2SinceYear']

for col in check_cols:
    print(col)
    print(sorted(merged_sales[col].unique()))


# In[26]:


merged_sales['CompetitionOpenSinceMonth'] = merged_sales['CompetitionOpenSinceMonth'].convert_dtypes()
merged_sales['CompetitionOpenSinceYear'] = merged_sales['CompetitionOpenSinceYear'].convert_dtypes()
merged_sales['Promo2SinceWeek'] = merged_sales['Promo2SinceWeek'].convert_dtypes()
merged_sales['Promo2SinceYear'] = merged_sales['Promo2SinceYear'].convert_dtypes()


# In[27]:


merged_sales.info()


# In[28]:


merged_sales.info()


# In[29]:


## mean sales including entries for days stores are closed
merged_sales['Sales'].mean()


# In[30]:


## mean sales for only days stores are open
merged_sales.loc[merged_sales['Open'] == 1, 'Sales'].mean()


# In[31]:


## confirming all entries where the store is  marked as closed have 0 sales
merged_sales.loc[merged_sales["Open"] == 0, ['Sales', 'Customers']].value_counts()


# In[32]:


## creating new sales dataframe with only entries for days stores are open
sales = merged_sales.drop(index=(merged_sales[merged_sales["Open"] == 0]).index, axis=1)


# In[33]:


sales['Open'].value_counts()


# In[34]:


sales.drop(columns=["Open"], inplace=True)


# In[35]:


sales.plot(y=['Sales', 'Customers', 'CompetitionDistance'], 
           kind='box', subplots=True, layout=(2,2), figsize=(15,15))


# In[36]:


def calculate_outlier(df,column): ## function for calculating outliers
    Q3 = df[column].quantile(0.75)
    Q1 = df[column].quantile(0.25)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    percent_outliers = round(((df[df[column] > upper].shape[0]) + (df[df[column] < lower].shape[0])) / df.shape[0] * 100, 2)
    return lower, upper, percent_outliers


# In[37]:


col = 'Sales'
lower_sales, upper_sales, percent_outliers_sales = calculate_outlier(sales, col)

print("lower band = " + str(lower_sales))
print("upper band = " + str(upper_sales))
print("percentage of sales that are outliers = " + str(percent_outliers_sales) + "%")


# In[38]:


sales[sales[col] > upper_sales]


# In[39]:


sales_outliers_by_month = pd.pivot_table((sales.loc[sales[col] > upper_sales]), index='Month', values='Sales', aggfunc='count')

sales_outliers_by_month.plot(y='Sales', kind='bar', figsize=(10,5), title="# of Sales Outlier Entries by Month")
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
plt.show()


# In[40]:


sales_outliers_by_stype = pd.pivot_table((sales.loc[sales[col] > upper_sales]), index='StoreType', values='Sales', aggfunc='count')

sales_outliers_by_stype.plot(y='Sales', kind='bar', figsize=(6,6), 
                             title="# of Sales Outlier Entries by Store Type", 
                             color=['blue','red','green','orange'])
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
plt.show()


# In[41]:


sales_treated = sales.copy()


# In[42]:


sales_treated.loc[sales_treated[col] > upper_sales, 'Sales'] = 13612


# In[43]:


sales_treated[sales_treated['Sales'] > 13612] ## double-checking our imputation worked


# In[44]:


col = 'Customers'
lower_cust, upper_cust, percent_outliers_cust = calculate_outlier(sales_treated, col)

print(str(lower_cust) + ", " + str(upper_cust) +", " + str(percent_outliers_cust) + "%")


# In[45]:


sales_treated[sales_treated['Customers'] > upper_cust]


# In[46]:


sales_treated[(sales_treated['Customers'] > upper_cust) & (sales_treated['Sales'] == 13612)]


# In[47]:


cust_outliers_by_month = pd.pivot_table((sales_treated.loc[sales_treated[col] > upper_cust]), index='Month', values='Customers', aggfunc='count')

cust_outliers_by_month.plot(y='Customers', kind='bar', figsize=(10,5), title="# of Customer Outlier Entries by Month")
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
plt.show()


# In[48]:


cust_outliers_by_stype = pd.pivot_table((sales_treated.loc[sales_treated[col] > upper_cust]), index='StoreType', values='Customers', aggfunc='count')

cust_outliers_by_stype.plot(y='Customers', kind='bar', figsize=(6,6), 
                             title="# of Customer Outlier Entries by Store Type", 
                             color=['blue','red','green','orange'])
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
plt.show()


# In[49]:


sales_treated.loc[sales_treated['Customers'] > upper_cust, 'Customers'] = 1454


# In[50]:


sales_treated.loc[sales_treated['Customers'] > upper_cust, 'Customers']


# In[51]:


sales_treated.isna().sum()


# In[52]:


(sales_treated.isna().sum() * 100 / sales_treated.shape[0]).round(2)   ## missing values as a % of all values in the column


# In[53]:


print(sales_treated[sales_treated['Promo2'] == 0].shape[0])
print(sales_treated['Promo2SinceWeek'].isna().sum())
print(sales_treated['Promo2SinceYear'].isna().sum())


# In[54]:


mean_type_a = round(stores_lookup.loc[(stores_lookup['StoreType'] == 'a'), 'CompetitionDistance'].mean(), 1)
mean_type_b = round(stores_lookup.loc[(stores_lookup['StoreType'] == 'b'), 'CompetitionDistance'].mean(), 1)
mean_type_c = round(stores_lookup.loc[(stores_lookup['StoreType'] == 'c'), 'CompetitionDistance'].mean(), 1)
mean_type_d = round(stores_lookup.loc[(stores_lookup['StoreType'] == 'd'), 'CompetitionDistance'].mean(), 1)

print("The mean Compeition Distance for stores of type A is " + str(mean_type_a))
print("The mean Compeition Distance for stores of type B is " + str(mean_type_b))
print("The mean Compeition Distance for stores of type C is " + str(mean_type_c))
print("The mean Compeition Distance for stores of type D is " + str(mean_type_d))


# In[55]:


sales_treated.loc[sales_treated['StoreType'] == 'a'] = sales_treated.loc[sales_treated['StoreType'] == 'a'].fillna(value={"CompetitionDistance" : mean_type_a})
sales_treated.loc[sales_treated['StoreType'] == 'b'] = sales_treated.loc[sales_treated['StoreType'] == 'b'].fillna(value={"CompetitionDistance" : mean_type_b}) 
sales_treated.loc[sales_treated['StoreType'] == 'c'] = sales_treated.loc[sales_treated['StoreType'] == 'c'].fillna(value={"CompetitionDistance" : mean_type_c}) 
sales_treated.loc[sales_treated['StoreType'] == 'd'] = sales_treated.loc[sales_treated['StoreType'] == 'd'].fillna(value={"CompetitionDistance" : mean_type_d}) 


# In[56]:


sales_treated.isna().sum()


# In[57]:


sales_treated.loc[sales_treated['PromoInterval'].isna(), 'PromoInterval'] = "NA"


# In[58]:


sales_treated['PromoInterval'].value_counts()


# In[59]:


sales_treated.loc[sales_treated['CompetitionOpenSinceYear'].isna(), 'CompetitionOpenSinceYear'] = dt.datetime.now().year

sales_treated.loc[sales_treated['Promo2SinceYear'].isna(), 'Promo2SinceYear'] = dt.datetime.now().year

sales_treated.loc[sales_treated['CompetitionOpenSinceMonth'].isna(), 'CompetitionOpenSinceMonth'] = dt.datetime.now().month

sales_treated.loc[sales_treated['Promo2SinceWeek'].isna(), 'Promo2SinceWeek'] = dt.datetime.now().isocalendar()[1]


# In[60]:


sales_treated.isna().sum()


# In[61]:


(sales_treated['Customers'] >= sales_treated['Sales']).value_counts()


# In[62]:


sales_treated[sales_treated['Customers'] >= sales_treated['Sales']]


# In[63]:


sales_treated[sales_treated['Customers'] > sales_treated['Sales']]


# In[64]:


sales_treated['UPT'] = sales_treated['Sales'] / sales_treated['Customers']


# In[65]:


sales_treated['UPT'].isna().sum()


# In[66]:


sales_treated.loc[sales_treated['UPT'].isna(), 'UPT'] = 0


# In[67]:


sales_treated['UPT'].isna().sum()


# In[68]:


sales['UPT'] = sales['Sales'] / sales['Customers']
sales.loc[sales['UPT'].isna(), 'UPT'] = 0


# In[69]:


merged_sales[['Sales', 'Customers', 'CompetitionDistance']].describe() ## BEFORE cleaning


# In[70]:


sales_treated[['Sales', 'Customers', 'CompetitionDistance', 'UPT']].describe() ## AFTER cleaning


# In[71]:


merged_sales[['Sales', 'Customers', 'CompetitionDistance']].skew() ## BEFORE cleaning


# In[72]:


sales_treated[['Sales', 'Customers', 'CompetitionDistance', 'UPT']].skew() ## AFTER cleaning


# In[73]:


merged_sales[['Sales', 'Customers', 'CompetitionDistance']].kurtosis() ## BEFORE cleaning


# In[74]:


sales_treated[['Sales', 'Customers', 'CompetitionDistance', 'UPT']].kurtosis() ## AFTER cleaning


# In[75]:


fig, axes = plt.subplots(nrows=1, ncols=2)

sales_treated.hist(column='Sales', bins='sturges', ax=axes[0])
sales_treated.hist(column='Customers', bins='sturges', ax=axes[1])
fig.set_size_inches(15, 5)
plt.show()


# In[76]:


assortment_pivot_total_sales = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), ## Excluding 2015 data
               index='Month', values='Sales', columns='Assortment', aggfunc=np.sum)
assortment_pivot_total_sales


# In[77]:


assortment_pivot_total_sales.plot(kind='line', title='Total Sales by Month and Store Assortment', figsize=(7,8), grid=True)
plt.show()


# In[78]:


pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), index='Assortment', values='Store', aggfunc='count')


# In[79]:


assortment_pivot_avg_sales = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), index='Month', values='Sales', columns='Assortment', aggfunc=np.mean)
assortment_pivot_avg_sales


# In[80]:


assortment_pivot_avg_sales.plot(kind='line', title='Average Sales by Month and Store Assortment', figsize=(7,5), grid=True)
plt.show()


# In[81]:


assortment_pivot_avg_UPT = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), 
                                     index='Month', values='UPT', columns='Assortment', aggfunc=np.mean)
assortment_pivot_avg_UPT_outliers = pd.pivot_table((sales[sales['Year'] < 2015]), 
                                     index='Month', values='UPT', columns='Assortment', aggfunc=np.mean)

fig, axes = plt.subplots(nrows=1, ncols=2)

assortment_pivot_avg_UPT.plot(kind='line', title='Average UPT by Month and Store Assortment (no outliers)', figsize=(7,5), grid=True, ax=axes[0])
assortment_pivot_avg_UPT_outliers.plot(kind='line', title='Average UPT by Month and Store Assortment (outliers incl.)', figsize=(7,5), grid=True, ax=axes[1])
fig.set_size_inches(15, 5)
plt.show()


# In[82]:


pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), index='StoreType', values='Store', aggfunc='count')


# In[83]:


stype_pivot_avg_sales = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), ## Excluding 2015 data
               index='Month', values='Sales', columns='StoreType', aggfunc=np.mean)
stype_pivot_avg_sales


# In[84]:


stype_pivot_avg_sales.plot(kind='line', title='Average Sales by Month and Store Type', figsize=(7,5), grid=True)
plt.show()


# In[85]:


stype_pivot_avg_UPT = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), 
                                     index='Month', values='UPT', columns='StoreType', aggfunc=np.mean)
stype_pivot_avg_UPT_outliers = pd.pivot_table((sales[sales['Year'] < 2015]), 
                                     index='Month', values='UPT', columns='StoreType', aggfunc=np.mean)

fig, axes = plt.subplots(nrows=1, ncols=2)

stype_pivot_avg_UPT.plot(kind='line', title='Average UPT by Month and Store Type (no outliers)', figsize=(7,5), grid=True, ax=axes[0])
stype_pivot_avg_UPT_outliers.plot(kind='line', title='Average UPT by Month and Store Type (outliers incl.)', figsize=(7,5), grid=True, ax=axes[1])
fig.set_size_inches(15, 5)
plt.show()


# In[86]:


stype_pivot_total_cust = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), index='Month', columns='StoreType', values='Customers', aggfunc='count')
stype_pivot_avg_cust = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]), index='Month', columns='StoreType', values='Customers', aggfunc=np.mean)

fig, axes = plt.subplots(nrows=1, ncols=2)

stype_pivot_total_cust.plot(kind='line', title='Total Customers by Month and Store Type', figsize=(7,5), grid=True, ax=axes[0])
stype_pivot_avg_cust.plot(kind='line', title='Average Customers by Month and Store Type', figsize=(7,5), grid=True, ax=axes[1])
fig.set_size_inches(15, 5)
plt.show()


# In[87]:


stype_pivot_avg_compdist = pd.pivot_table((sales_treated[sales_treated['Year'] < 2015]),
                                         index='StoreType', values='CompetitionDistance', aggfunc=np.mean)

stype_pivot_avg_compdist.plot(kind='bar', rot=0)
plt.show()


# In[88]:


sales_treated.plot(x='CompetitionDistance', y='UPT', kind='scatter', figsize=(8,6))
plt.show()


# In[89]:


corr = sales_treated.corr()

plt.figure(figsize = (15,8))
sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, center=0, cmap="YlGnBu", annot=True)
plt.show()


# In[ ]:




