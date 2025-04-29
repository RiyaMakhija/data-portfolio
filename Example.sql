use mydatabase;

select * from Product

select Category, sum(Cost_per_box) as Total_Cost from Product 
group by Category

select * from Shipments

select Order_Status, sum(Amount) as Total_Amount from Shipments 
group by Order_Status

with Ranked as (
select Product, Category,Cost_per_box, ROW_NUMBER() over (Partition by Category order by Cost_per_box asc) as rank
from Product 
)

select * from Ranked where rank <=5

with ranked as (
select *,ROW_NUMBER() over (order by Cost_per_box asc) as rank from Product)

select * from ranked 

select  *,sum(Amount) over(partition by Order_Status order by Shipdate desc) as rank from Shipments

where Shipdate>=DATEADD(DAY,-30,'2024-10-01') order by Shipdate desc
select * from Calendar

select * from(
select sum(s.Amount) as Total_amount,l.Region,c.Year,
Row_number() over (partition by l.Region order by sum(s.Amount) desc) as rank

from Shipments s left join Location l on s.GID=l.GID left join Calendar c 
on c.cal_date=s.Shipdate 
group by l.Region,c.year ) as ranked
where rank =1 order by Total_amount desc