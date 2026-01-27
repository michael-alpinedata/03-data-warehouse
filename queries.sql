```sql 
-- question 1
-- create external table
CREATE OR REPLACE EXTERNAL TABLE `dtc-zoomcamp-2026.nytaxi.external_yellow_tripdata_2024_hw`
OPTIONS (
  format='PARQUET',
  uris=[
    'gs://dtc-data-lake-nyc-buket-hw/yellow/yellow_tripdata_2024-*.parquet'    
  ]
)

-- create table
CREATE OR REPLACE TABLE `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`
AS SELECT * FROM `dtc-zoomcamp-2026.nytaxi.external_yellow_tripdata_2024_hw`;
```


```sql 
-- question 2
-- external table
SELECT COUNT(DISTINCT(PULocationID))
FROM `dtc-zoomcamp-2026.nytaxi.external_yellow_tripdata_2024_hw`;

-- materialized table
SELECT COUNT(DISTINCT(PULocationID))
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`;
```


```sql 
-- question 3
SELECT PULocationID
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`;

SELECT PULocationID, DOLocationID
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`;
```


```sql 
-- question 4 
SELECT COUNT(*)
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`
WHERE fare_amount = 0;
```

```sql 
-- question 5
CREATE OR REPLACE TABLE `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS 
SELECT * FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`;
```

```sql 
-- question 6
SELECT DISTINCT(VendorID)
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw`
WHERE '2024-03-01' <= DATE(tpep_dropoff_datetime) 
AND DATE(tpep_dropoff_datetime) <= '2024-03-15';

SELECT DISTINCT(VendorID)
FROM `dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw_partitioned_clustered`
WHERE '2024-03-01' <= DATE(tpep_dropoff_datetime) 
AND DATE(tpep_dropoff_datetime) <= '2024-03-15';
```

```sql 
-- question 9 
SELECT count(*)
FROM dtc-zoomcamp-2026.nytaxi.yellow_tripdata_2024_hw;
```