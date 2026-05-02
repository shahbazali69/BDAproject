@echo off
echo =======================================================
echo    BDA PROJECT - HADOOP MAPREDUCE (LOCAL MODE)
echo =======================================================

echo.
echo [1/4] Cleaning old output directories...
rd /s /q hadoop_kpis 2>nul
rd /s /q hadoop_categories 2>nul
rd /s /q hadoop_customers 2>nul

echo.
echo [2/4] Running Hadoop Jobs (This may take a few minutes)...

echo   -- Running KPIs Job --
call C:\hadoop\bin\hadoop.cmd jar C:\hadoop\share\hadoop\tools\lib\hadoop-streaming-3.2.4.jar -fs file:/// -jt local -input Cleaned_Ecommerce_Data.csv -output hadoop_kpis -mapper "python backend/hadoop/kpis/mapper.py" -reducer "python backend/hadoop/kpis/reducer.py"

echo   -- Running Categories Job --
call C:\hadoop\bin\hadoop.cmd jar C:\hadoop\share\hadoop\tools\lib\hadoop-streaming-3.2.4.jar -fs file:/// -jt local -input Cleaned_Ecommerce_Data.csv -output hadoop_categories -mapper "python backend/hadoop/categories/mapper.py" -reducer "python backend/hadoop/categories/reducer.py"

echo   -- Running Customers Job --
call C:\hadoop\bin\hadoop.cmd jar C:\hadoop\share\hadoop\tools\lib\hadoop-streaming-3.2.4.jar -fs file:/// -jt local -input Cleaned_Ecommerce_Data.csv -output hadoop_customers -mapper "python backend/hadoop/customers/mapper.py" -reducer "python backend/hadoop/customers/reducer.py"

echo.
echo [3/4] Exporting MapReduce output to MongoDB...
cd backend
..\venv\Scripts\python.exe export_to_mongo.py kpis ..\hadoop_kpis\part-00000
..\venv\Scripts\python.exe export_to_mongo.py categories ..\hadoop_categories\part-00000
..\venv\Scripts\python.exe export_to_mongo.py customers ..\hadoop_customers\part-00000
cd ..

echo.
echo [4/4] COMPLETE! Your MongoDB is now populated with real MapReduce data.
echo =======================================================
