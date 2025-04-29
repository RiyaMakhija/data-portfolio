use mydatabase

select p.PlatformName, h.HashtagName, t.FullDate, b.BrandName, f.PostText, f.SentimentScore from Fact_Posts f
left join Dim_Platform p on f.PlatformID=p.PlatformID left join Dim_Hashtag h on f.HashtagID=h.HashtagID
left join Dim_Time t on t.TimeID=f.TimeID left join Dim_Brand b on f.BrandID=b.BrandID where t.FullDate >'2025-02-01'


select distinct b.BrandName from Fact_Posts f left join Dim_Brand b on f.BrandID=b.BrandID 
where f.SentimentScore>0

select p.PlatformName,f.SentimentCategory,Count(distinct f.PostID) as Number_Of_Post from Fact_Posts f left join Dim_Platform p on f.PlatformID=p.PlatformID 
group by p.PlatformName,f.SentimentCategory
order by Number_Of_Post

select  Top 5 h.HashtagName,count(distinct f.PostID) as Number_Of_Post from Fact_Posts f 
inner join Dim_Hashtag h on f.HashtagID=h.HashtagID
group by h.HashtagName order by Number_Of_Post desc

select avg(f.SentimentScore) as Average_Of_SentimentScore, b.BrandName from Fact_Posts f inner join Dim_Brand b  on f.BrandID=b.BrandID
group by b.BrandName

select count(distinct f.PostID) as Number_Of_Posts,t.FullDate from Fact_Posts f left join Dim_Time t on f.TimeID=t.TimeID
group by t.FullDate
order by t.FullDate desc

with ranked as (

select count(distinct f.PostID) as Number_of_posts,h.HashtagName,p.PlatformName, 
Row_number() over (partition by p.PlatformName order by count(distinct f.PostID) desc) as rank 
from Fact_Posts f inner join Dim_Hashtag h on f.HashtagID=h.HashtagID
inner join Dim_Platform p on f.PlatformID=p.PlatformID
group by p.PlatformName,h.HashtagName
)

select * from ranked where rank <= 3 


----------------------------------------------------------------------

with ranked as (
select b.BrandName, count(*) as Positive_Posts
from Fact_Posts f inner join Dim_Brand b on f.BrandID=b.BrandID where f.SentimentScore>0
group by b.BrandName
)

select *, dense_rank() over (order by Positive_Posts desc) as rank from ranked
----------------------------------------------------------------------------------------------

select top 1 t.WeekDayName, Count(distinct f.PostID)as Number_of_posts from Fact_Posts f inner join Dim_Time t on f.TimeID=t.TimeID
group by t.WeekDayName
order by Number_of_posts desc

-----------------------------------------------------------------------------------------------------

select t.Hour,AVG(f.SentimentScore) as Average_score from Fact_Posts f inner join Dim_Time t on f.TimeID=t.TimeID
group by t.Hour

--------------------------------------------------------------------------------------------------------------

select avg(f.SentimentScore),b.BrandName,
case when avg(f.SentimentScore)>0.05 then 'Excellent' 
when avg(f.SentimentScore) between 0.02 and 0.05  then 'Good'
when avg(f.SentimentScore) < 0.02   then 'Needs Improvement' end as Brand_Performance from Fact_Posts  f 
inner join Dim_Brand b on f.BrandID=b.BrandID
 group by b.BrandName

 -----------------------------------------------------------------------------------------------------------


 select b.BrandName ,avg(f.SentimentScore) as Local_Score from Fact_Posts f inner join Dim_Brand b on f.BrandID=b.BrandID
 group by b.BrandName
 having avg(f.SentimentScore) >(select avg(SentimentScore) from Fact_Posts)
 order by Local_Score desc

 ----------------------------------------------------------------------------------------------------------------

 select h.HashtagName,f.Sentimentcategory from Fact_Posts f inner join Dim_Hashtag h on f.HashtagID=h.HashtagID
 where f.SentimentCategory in(select SentimentCategory from Fact_Posts where SentimentCategory='Negative')

 --------------------------------------------------------------------------------------------------------------------

 with ranked as (
 select b.Brandname, count(distinct f.PostID) as Number_of_posts,f.SentimentCategory from Fact_Posts f inner join Dim_Brand b on f.BrandID=b.BrandID
 group by b.BrandName, f.SentimentCategory
 having count(distinct f.PostID) >10
 )

 select * from ranked where SentimentCategory='Positive'

 ------------------------------------------------------------------------------------------------------------------------------

with ranked as (

select b.BrandName, t.Year, t.Month, avg(f.SentimentScore) as Average_Score,
count(distinct f.PostID) as number_of_posts from Fact_Posts f inner join Dim_Time t on f.TimeID=t.TimeID 
inner join Dim_Brand b on f.BrandID=b.BrandID 
group by b.BrandName,t.Year, t.Month
)

select BrandName,Year,Month,number_of_posts,Average_Score, row_number() over(partition by Year,Month order by Average_Score desc, number_of_posts desc) as rank 
from ranked 

------------------------------------------------------------------------------------------------------------------------------

with ranked as (

select h.HashtagName,avg(f.SentimentScore) *count(distinct f.PostID) as Engagement,t.Month, 
row_number() over (partition by Month order by  avg(f.SentimentScore) *count(distinct f.PostID) desc) as rank
from Fact_Posts f inner join Dim_Hashtag h on f.HashtagID=h.HashtagID inner join Dim_Time t on f.TimeID=t.TimeID
group by h.HashtagName,t.Month
)
select * from ranked order by rank 
---------------------------------------------------------------------------------------------------------------------------




