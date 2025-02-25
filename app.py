from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key in production
app.config['SESSION_COOKIE_SIZE_LIMIT'] = 4000  # Set a safe limit

# Sample quiz data - in a real app, you might load this from a database or file
QUIZ_DATA = [
    {
        "category": "Ingest Data with Microsoft Fabric",
        "questions": [
            {
                "question": "What is the primary purpose of using Dataflows Gen2 in Microsoft Fabric?",
                "options": [
                    "Data ingestion",
                    "Data transformation",
                    "Data storage",
                    "Data visualization"
                ],
                "correctAnswer": 1,
                "explanation": "Dataflows Gen2 are primarily used for transforming data within Microsoft Fabric, allowing for efficient data manipulation before it is stored or analyzed.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-dataflow-gen-2-fabric/4-dataflow-pipeline"
            },
            {
                "question": "What are the two broad categories of activities in a pipeline?",
                "options": [
                    "Data transformation activities and Control flow activities",
                    "Data processing activities and Control flow activities",
                    "Data ingestion activities and Data storage activities",
                    "Data extraction activities and Data transformation activities"
                ],
                "correctAnswer": 0,
                "explanation": "Pipelines consist of two main types of activities: data transformation activities, which handle data transfer and transformation, and control flow activities, which manage the execution logic of the pipeline.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-data-factory-pipelines-fabric/2-understand-fabric-pipeline"
            },
            {
                "question": "A team wants to reuse a pipeline to load data into different lakehouse folders dynamically. Which pipeline feature should they use?",
                "options": [
                    "Parameters",
                    "Variables",
                    "Triggers",
                    "Hardcoded folder names"
                ],
                "correctAnswer": 0,
                "explanation": "Parameters allow pipelines to accept dynamic values (e.g., folder names) at runtime, enabling reusability.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-data-factory-pipelines-fabric/2-understand-fabric-pipeline"
            },
            {
                "question": "What is the primary use of the Copy Data activity in a data pipeline?",
                "options": [
                    "To apply transformations to data during ingestion",
                    "To ingest data from an external source into a lakehouse file or table",
                    "To delete existing data before copying new data",
                    "To merge data from multiple sources"
                ],
                "correctAnswer": 1,
                "explanation": "The Copy Data activity is primarily used to ingest data from an external source into a lakehouse file or table without applying transformations.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-data-factory-pipelines-fabric/3-copy-data"
            },
            {
                "question": "When should you consider using a Data Flow activity instead of a Copy Data activity?",
                "options": [
                    "When you need to copy data directly between a source and destination",
                    "When you want to import raw data without transformations",
                    "When you need to apply transformations to the data as it is ingested",
                    "When you are using a graphical tool to configure the data source"
                ],
                "correctAnswer": 2,
                "explanation": "A Data Flow activity should be used when you need to apply transformations to the data as it is ingested or merge data from multiple sources.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-data-factory-pipelines-fabric/3-copy-data"
            },
            {
                "question": "What tool is used to define transformation steps for a Data Flow activity?",
                "options": [
                    "Azure Portal",
                    "Power Query",
                    "Spark Notebook",
                    "Graphical Copy Data tool"
                ],
                "correctAnswer": 1,
                "explanation": "Data Flow activities use Power Query for defining transformations.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-data-factory-pipelines-fabric/3-copy-data"
            },
            {
                "question": "Which architecture combines batch data loading with real-time data ingestion?",
                "options": [
                    "Data warehouse architecture",
                    "Lambda architecture",
                    "Event-driven architecture",
                    "Microservices architecture"
                ],
                "correctAnswer": 1,
                "explanation": "The lambda architecture combines the periodic loading of batch data for historical analysis with the ingestion of data streams for real-time analysis.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/2-define-real-time-analytics"
            },
            {
                "question": "Which Microsoft Fabric component is specifically designed for ingesting continuous real-time data?",
                "options": [
                    "Eventhouse",
                    "Power BI Dataset",
                    "Eventstream",
                    "KQL Database"
                ],
                "correctAnswer": 2,
                "explanation": "Eventstream in Microsoft Fabric is used to ingest real-time data from diverse sources as a continuous stream.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/2-define-real-time-analytics"
            },
            {
                "question": "What is the primary purpose of Activator in Microsoft Fabric's Real-Time Intelligence?",
                "options": [
                    "Automate data transformation pipelines",
                    "Trigger alerts based on streaming data thresholds",
                    "Generate batch analytics reports",
                    "Manage data warehouse indexing"
                ],
                "correctAnswer": 1,
                "explanation": "Activator enables defining automated alerts and actions when specific conditions occur in real-time data streams.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/2-define-real-time-analytics"
            },
            {
                "question": "Which transformation in Eventstreams is used to combine data from two streams based on a matching condition between them?",
                "options": [
                    "Join",
                    "Union",
                    "Group by",
                    "Expand"
                ],
                "correctAnswer": 0,
                "explanation": "The Join transformation is designed to combine data from two streams using a matching condition, unlike Union, which merges streams with shared fields.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/3a-define-real-time-hub"
            },
            {
                "question": "What is a KQL database?",
                "options": [
                    "A data store optimized for batch processing that hosts static tables",
                    "A real-time optimized data store that hosts tables and functions",
                    "A query language tool for processing historical data",
                    "A storage system focused only on table management and data ingestion"
                ],
                "correctAnswer": 1,
                "explanation": "A KQL database is specifically designed as a real-time optimized data store that hosts a collection of tables, stored functions, materialized views, and shortcuts.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/4-write-queries-kusto-query-language"
            },
            {
                "question": "What does the 'take' operator do in a KQL query?",
                "options": [
                    "Filters data based on a condition",
                    "Retrieves a specified number of rows from a table",
                    "Aggregates data",
                    "Joins two tables together"
                ],
                "correctAnswer": 1,
                "explanation": "'take' is an operator in KQL that retrieves a specified number of rows from a table.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/4-write-queries-kusto-query-language"
            },
            {
                "question": "Which T-SQL statement is equivalent to the KQL query 'stock | take 10'?",
                "options": [
                    "SELECT * FROM stock LIMIT 10",
                    "SELECT TOP 10 * FROM stock",
                    "FETCH FIRST 10 ROWS FROM stock",
                    "SELECT * FROM stock WHERE ROWNUM <= 10"
                ],
                "correctAnswer": 1,
                "explanation": "The 'SELECT TOP 10 * FROM stock' is the SQL equivalent of the KQL 'take 10' operator.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/4-write-queries-kusto-query-language"
            },
            {
                "question": "What type of operations can transformations in an eventstream perform?",
                "options": [
                    "Only filtering data",
                    "Only aggregating data",
                    "Filtering, joining, aggregating, and grouping",
                    "Storing data in destinations"
                ],
                "correctAnswer": 2,
                "explanation": "Transformations can perform a variety of operations including filtering, joining, aggregating, and grouping, as well as temporal windowing functions.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/2-eventstream-components"
            },
            {
                "question": "What is the primary purpose of the Derived Stream destination in Microsoft Fabric Eventstreams?",
                "options": [
                    "To store raw event data in a KQL database",
                    "To preprocess events before ingestion into a lakehouse",
                    "To represent the altered default stream after applying stream operations",
                    "To trigger automated actions based on streaming data values"
                ],
                "correctAnswer": 2,
                "explanation": "The Derived Stream destination is created after applying stream operations like Filter or Manage Fields to an eventstream, representing the altered default stream.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/3-setup-eventstreams"
            },
            {
                "question": "Which window type groups events based on a gap of inactivity?",
                "options": [
                    "Tumbling",
                    "Sliding",
                    "Session",
                    "Hopping"
                ],
                "correctAnswer": 2,
                "explanation": "Session windows group events into variable and non-overlapping intervals based on a gap of inactivity.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/4-route-event-data-to-destinations"
            },
            {
                "question": "What keyword should you use to retrieve only specific columns in a KQL query?",
                "options": [
                    "filter",
                    "select",
                    "project",
                    "retrieve"
                ],
                "correctAnswer": 2,
                "explanation": "The 'project' keyword is used in KQL to specify which columns to retrieve from a dataset, helping to optimize performance by minimizing the data returned.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/3-kql-best-practices"
            },
            {
                "question": "Which KQL query correctly retrieves events ingested into the Automotive table within the past hour when the data lacks a timestamp?",
                "options": [
                    "Automotive | where pickup_datetime > ago(1h)",
                    "Automotive | where ingestion_time() > ago(1h)",
                    "Automotive | where current_utc_time() - ingestion_time() < 1h",
                    "Automotive | where timestamp > ago(1h)"
                ],
                "correctAnswer": 1,
                "explanation": "The ingestion_time() function filters data based on when it was loaded into the table, which is essential when the data itself lacks a timestamp.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/3-kql-best-practices"
            },
            {
                "question": "How does a materialized view populate itself when created without the backfill option?",
                "options": [
                    "The view is immediately populated with all existing data.",
                    "The view is populated incrementally as new data is ingested.",
                    "Existing data is deleted from the source table.",
                    "The view creation fails unless backfill is enabled."
                ],
                "correctAnswer": 1,
                "explanation": "Materialized views created without the backfill option are populated incrementally as new data is ingested, rather than processing existing data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/4-advanced-features"
            },
            {
                "question": "Which scenario best justifies using a materialized view instead of a stored function?",
                "options": [
                    "Reusing a parameterized query with variable inputs",
                    "Creating an on-demand summary of historical data",
                    "Automatically maintaining a pre-aggregated dataset for frequent queries",
                    "Performing real-time transformations during data ingestion"
                ],
                "correctAnswer": 2,
                "explanation": "Materialized views are designed to maintain pre-aggregated datasets efficiently, which is ideal for frequent queries requiring summarized data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/4-advanced-features"
            }
        ]
    },
    {
        "category": "Implement a Lakehouse with Microsoft Fabric",
        "questions": [
            {
                "question": "What is the primary purpose of OneLake in Microsoft Fabric?",
                "options": [
                    "To provide a unified storage solution for all analytics engines in Fabric",
                    "To act as a data integration tool for moving data between systems",
                    "To serve as a standalone data warehouse solution",
                    "To manage compute resources for Fabric workspaces"
                ],
                "correctAnswer": 0,
                "explanation": "OneLake is designed to provide a single, integrated storage environment for all analytics engines in Fabric, eliminating the need to move or copy data between systems.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/2-explore-analytics-fabric"
            },
            {
                "question": "What feature of OneLake allows users to reference existing cloud data without copying it?",
                "options": [
                    "Data lineage",
                    "Shortcuts",
                    "Dataflows",
                    "Workspaces"
                ],
                "correctAnswer": 1,
                "explanation": "Shortcuts in OneLake enable users to create embedded references to existing data sources, facilitating easy access without duplication.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/2-explore-analytics-fabric"
            },
            {
                "question": "What is the primary purpose of a workspace in Microsoft Fabric?",
                "options": [
                    "To store data permanently",
                    "To create and manage collaborative items",
                    "To perform data analysis",
                    "To configure Azure settings"
                ],
                "correctAnswer": 1,
                "explanation": "A workspace serves as a collaborative environment for creating and managing items like lakehouses, warehouses, and reports.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/4-use-fabric"
            },
            {
                "question": "What feature do lakehouses support to ensure data consistency and integrity?",
                "options": [
                    "Schema-on-write",
                    "ACID transactions through Delta Lake formatted tables",
                    "Only read-only access",
                    "Data replication across multiple regions"
                ],
                "correctAnswer": 1,
                "explanation": "Lakehouses support ACID transactions, which are essential for maintaining data consistency and integrity.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-lakehouses/2-fabric-lakehouse"
            },
            {
                "question": "How is access to a Fabric lakehouse typically managed?",
                "options": [
                    "Through individual user accounts only",
                    "Using workspace roles and item-level sharing",
                    "Exclusively via API keys",
                    "Through Azure Active Directory groups only"
                ],
                "correctAnswer": 1,
                "explanation": "Access to a Fabric lakehouse is managed through workspace roles for collaborators and item-level sharing for read-only needs.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-lakehouses/2-fabric-lakehouse"
            },
            {
                "question": "What is the purpose of the partitionBy method when saving a DataFrame?",
                "options": [
                    "To specify the file format",
                    "To optimize performance by partitioning data",
                    "To define the schema",
                    "To overwrite existing files"
                ],
                "correctAnswer": 1,
                "explanation": "The partitionBy method is used to optimize performance by partitioning the data into separate folders based on the specified column values.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-apache-spark-work-files-lakehouse/4-dataframe"
            },
            {
                "question": "Which method is used to save a dataframe as a new table in Spark SQL?",
                "options": [
                    "spark.catalog.createTable",
                    "df.createOrReplaceTempView",
                    "df.write.format('delta').saveAsTable",
                    "spark.catalog.createExternalTable"
                ],
                "correctAnswer": 2,
                "explanation": "The method df.write.format('delta').saveAsTable is specifically used to save a dataframe as a new table in Spark SQL.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-apache-spark-work-files-lakehouse/5-spark-sql"
            },
            {
                "question": "What happens when you delete an external table from Spark Catalog?",
                "options": [
                    "Both the metadata and data files are deleted",
                    "Only the metadata is deleted from the catalog, while the data files remain intact in their storage location",
                    "The metadata is archived and the data files are deleted",
                    "The metadata and data files are both archived, and can be restored later"
                ],
                "correctAnswer": 1,
                "explanation": "Deleting an external table only removes the metadata from the catalog, while the underlying data remains intact.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-apache-spark-work-files-lakehouse/5-spark-sql"
            },
            {
                "question": "What is the primary benefit of Delta tables in Microsoft Fabric lakehouses?",
                "options": [
                    "They only support batch data processing.",
                    "They provide ACID transaction support.",
                    "They can only store static data.",
                    "They do not support data versioning."
                ],
                "correctAnswer": 1,
                "explanation": "Delta tables provide ACID transaction support, ensuring that data modifications are atomic, consistent, isolated, and durable.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/2-understand-delta-lake"
            },
            {
                "question": "What is the purpose of the _delta_log folder in a Delta table?",
                "options": [
                    "To store Parquet data files",
                    "To log transaction details in JSON format",
                    "To store metadata for unstructured data",
                    "To cache query results for faster access"
                ],
                "correctAnswer": 1,
                "explanation": "The _delta_log folder contains transaction logs in JSON format, which are used to track changes and ensure ACID compliance.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/2-understand-delta-lake"
            },
            {
                "question": "What happens to the underlying data files when a managed table is deleted in a Fabric lakehouse?",
                "options": [
                    "They are retained",
                    "They are deleted",
                    "They are archived",
                    "They are moved to another location"
                ],
                "correctAnswer": 1,
                "explanation": "When a managed table is deleted, both the table definition and the underlying data files are deleted from the lakehouse.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/3-create-delta-tables"
            },
            {
                "question": "What is the purpose of the OptimizeWrite function in Delta Lake?",
                "options": [
                    "To delete old data files",
                    "To reduce the number of small files written",
                    "To partition data into subfolders",
                    "To enable time travel for data"
                ],
                "correctAnswer": 1,
                "explanation": "OptimizeWrite helps in writing fewer larger files instead of many small files, addressing the small file problem.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/3b-optimize-delta-tables"
            },
            {
                "question": "What does the VACUUM command do in Delta Lake?",
                "options": [
                    "It consolidates small files into larger ones",
                    "It removes old data files that are no longer referenced",
                    "It enables faster reads from the compute engines",
                    "It partitions data into subfolders"
                ],
                "correctAnswer": 1,
                "explanation": "The VACUUM command is used to remove old data files that are not referenced in the transaction log, helping to manage storage.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/3b-optimize-delta-tables"
            },
            {
                "question": "Which command is used to view the history of changes made to a delta table?",
                "options": [
                    "SHOW HISTORY",
                    "DESCRIBE HISTORY",
                    "VIEW HISTORY",
                    "GET HISTORY"
                ],
                "correctAnswer": 1,
                "explanation": "The DESCRIBE HISTORY command is specifically used to view the history of transactions applied to a delta table.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/4-work-delta-data"
            },
            {
                "question": "How can you retrieve data from a specific version of a delta table?",
                "options": [
                    "Using the versionAsOf option",
                    "Using the timestampAsOf option",
                    "Using the version option",
                    "Using the timeTravel option"
                ],
                "correctAnswer": 0,
                "explanation": "To retrieve data from a specific version of a delta table, you can use the versionAsOf option when reading the delta file location into a dataframe.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/work-delta-lake-tables-fabric/4-work-delta-data"
            },
            {
                "question": "What is the primary purpose of the bronze layer in the medallion architecture?",
                "options": [
                    "To store data in a refined format",
                    "To validate and clean the data",
                    "To serve as the landing zone for raw data",
                    "To aggregate data for analytics"
                ],
                "correctAnswer": 2,
                "explanation": "The bronze layer serves as the initial landing zone for all data, where it is stored in its original format without any changes.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/2-describe-medallion-architecture"
            },
            {
                "question": "What is the primary benefit of using the medallion architecture in a lakehouse?",
                "options": [
                    "It replaces existing data models entirely",
                    "It ensures data reliability and consistency as it moves through layers",
                    "It eliminates the need for data transformation tools",
                    "It restricts data access to a single team"
                ],
                "correctAnswer": 1,
                "explanation": "The medallion architecture ensures data reliability and consistency as it moves through different layers, improving data quality and making it easier to analyze.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/2-describe-medallion-architecture"
            },
            {
                "question": "Which layer in the medallion architecture is typically modeled in a star schema?",
                "options": [
                    "Bronze",
                    "Silver",
                    "Gold",
                    "Raw"
                ],
                "correctAnswer": 2,
                "explanation": "The Gold layer is modeled in a star schema, which is optimized for reporting.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/3-implement-medallion-archecture-fabric"
            },
            {
                "question": "What is the purpose of the SQL analytics endpoint in Fabric?",
                "options": [
                    "To create new data layers in the medallion architecture",
                    "To write queries, manage the semantic model, and query data visually",
                    "To generate cleansed data for third-party applications",
                    "To connect directly to Power BI without a semantic model"
                ],
                "correctAnswer": 1,
                "explanation": "The SQL analytics endpoint allows users to write queries, manage the semantic model, and utilize a visual query experience.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/4-query-report-data"
            },
            {
                "question": "How does Direct Lake mode benefit data analysts using Power BI?",
                "options": [
                    "It allows for real-time data processing without caching",
                    "It provides a static view of the data in the lakehouse",
                    "It caches frequently used data and refreshes it as needed",
                    "It requires manual updates to the semantic model"
                ],
                "correctAnswer": 2,
                "explanation": "Direct Lake mode caches often-used data and refreshes it as required, enhancing performance and ensuring up-to-date access to lakehouse data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/4-query-report-data"
            }
        ]
    },
    {
        "category": "Implement Real-Time Intelligence with Microsoft Fabric",
        "questions": [
            {
                "question": "Which characteristic describes a data stream in real-time analytics?",
                "options": [
                    "Data records are fixed and do not change",
                    "Data is added to the stream perpetually",
                    "Data streams are only processed once a day",
                    "Data records do not include time-based information"
                ],
                "correctAnswer": 1,
                "explanation": "A key characteristic of a data stream in real-time analytics is that it is unbounded, meaning data is continuously added to the stream without a predefined limit.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/2-define-real-time-analytics"
            },
            {
                "question": "How can the results of streaming data processing be used?",
                "options": [
                    "To support real-time automation or visualization.",
                    "To archive data in a cold storage solution.",
                    "To perform batch processing of historical data.",
                    "To generate static reports for regulatory compliance."
                ],
                "correctAnswer": 0,
                "explanation": "The results of streaming data processing can be used to support real-time (or near real-time) automation or visualization, enabling immediate insights and actions.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/2-define-real-time-analytics"
            },
            {
                "question": "What is the primary purpose of the Microsoft Fabric Real-Time Intelligence solution?",
                "options": [
                    "To provide a centralized place for managing real-time data sources",
                    "To create and manage virtual machines in Azure",
                    "To deploy highly available web applications",
                    "To store and analyze batch data in a data warehouse"
                ],
                "correctAnswer": 0,
                "explanation": "The Microsoft Fabric Real-Time Intelligence solution is designed to provide an end-to-end streaming solution for real-time data analysis, including managing real-time data sources.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/3-describe-kusto-databases-tables"
            },
            {
                "question": "Which Eventstreams destination allows direct KQL analysis of raw event data?",
                "options": [
                    "Lakehouse",
                    "Derived stream",
                    "Eventhouse",
                    "Fabric Activator"
                ],
                "correctAnswer": 2,
                "explanation": "The Eventhouse destination is specifically meant for ingesting real-time event data, allowing for analysis using Kusto Query Language.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/3a-define-real-time-hub"
            },
            {
                "question": "What does the Expand transformation do in eventstreams?",
                "options": [
                    "Groups array values into a single row",
                    "Creates a new row for each value within an array",
                    "Removes array values from the stream",
                    "Combines multiple arrays into one array"
                ],
                "correctAnswer": 1,
                "explanation": "The Union transformation is used to connect multiple nodes and combine events with shared fields into one table.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/3a-define-real-time-hub"
            },
            {
                "question": "What is a KQL database primarily used for in an eventhouse?",
                "options": [
                    "Storing static data",
                    "Hosting a collection of tables and functions for real-time data analysis",
                    "Performing batch processing of data",
                    "Creating visual reports"
                ],
                "correctAnswer": 1,
                "explanation": "A KQL database is designed to host tables and functions that facilitate real-time data analysis.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/4-write-queries-kusto-query-language"
            },
            {
                "question": "What role do Rules play in Activator?",
                "options": [
                    "They define the structure of events",
                    "They set conditions for triggering actions",
                    "They represent business objects",
                    "They map properties to event data"
                ],
                "correctAnswer": 1,
                "explanation": "Rules are crucial in Activator as they define the conditions under which actions are triggered based on property values.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-kusto-fabric/4c-activator"
            },
            {
                "question": "What is the primary function of Microsoft Fabric eventstreams?",
                "options": [
                    "To store data in a database",
                    "To create a pipeline of events from sources to destinations",
                    "To manage infrastructure for applications",
                    "To write complex code for data processing"
                ],
                "correctAnswer": 1,
                "explanation": "Microsoft Fabric eventstreams are designed to facilitate the movement of event data from various sources to different destinations, functioning like a conveyor belt.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/2-eventstream-components"
            },
            {
                "question": "Which window type divides incoming events into fixed and nonoverlapping intervals?",
                "options": [
                    "Sliding windows",
                    "Session windows",
                    "Tumbling windows",
                    "Hopping windows"
                ],
                "correctAnswer": 2,
                "explanation": "Tumbling windows are characterized by dividing events into fixed and nonoverlapping intervals based on their arrival time.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/4-route-event-data-to-destinations"
            },
            {
                "question": "What is the function of the Union transformation in eventstream processing?",
                "options": [
                    "To filter events based on specific criteria",
                    "To connect two or more nodes and combine events with shared fields",
                    "To calculate aggregations over a specified time period",
                    "To create new rows for each value in an array"
                ],
                "correctAnswer": 1,
                "explanation": "The Union transformation is used to connect multiple nodes and combine events that share the same fields, effectively merging data streams.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/4-route-event-data-to-destinations"
            },
            {
                "question": "What is the purpose of the grouping key in the Group by transformation?",
                "options": [
                    "To define the length of each window interval",
                    "To shift the start and end of each window interval",
                    "To specify the columns to group events by",
                    "To filter events based on a condition"
                ],
                "correctAnswer": 2,
                "explanation": "The grouping key in the Group by transformation specifies one or more columns in the event data to group events by, such as sensor ID or item category.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/explore-event-streams-microsoft-fabric/4-route-event-data-to-destinations"
            },
            {
                "question": "What is required to create an eventhouse in Microsoft Fabric?",
                "options": [
                    "A Fabric capacity that supports Real-Time Intelligence Fabric capability",
                    "A KQL database already created",
                    "A sample dataset imported",
                    "An Azure Event Hub configured"
                ],
                "correctAnswer": 0,
                "explanation": "Creating an eventhouse requires a workspace with a Fabric capacity that supports the Real-Time Intelligence Fabric capability.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/2-get-started-with-kql-queries"
            },
            {
                "question": "Which KQL query retrieves the first 100 rows from the Automotive table?",
                "options": [
                    "SELECT * FROM Automotive LIMIT 100",
                    "Automotive | take 100",
                    "Automotive | limit 100",
                    "SELECT TOP 100 * FROM Automotive"
                ],
                "correctAnswer": 1,
                "explanation": "The KQL query 'Automotive | take 100' is specifically designed to retrieve a sample of 100 rows from the Automotive table.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/2-get-started-with-kql-queries"
            },
            {
                "question": "What is the purpose of KQL Querysets in eventhouses?",
                "options": [
                    "To store KQL databases",
                    "To simplify query development with sample syntax and coding utilities",
                    "To visualize query results in Power BI",
                    "To import data from static locations"
                ],
                "correctAnswer": 1,
                "explanation": "KQL Querysets are designed to simplify query development by providing sample syntax and coding utilities for users.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-kql-database-microsoft-fabric/2-get-started-with-kql-queries"
            },
            {
                "question": "What is required to create a real-time dashboard in Microsoft Fabric?",
                "options": [
                    "A static data source",
                    "A source of real-time data",
                    "A SQL database",
                    "A data warehouse"
                ],
                "correctAnswer": 1,
                "explanation": "A real-time dashboard requires a source of real-time data to function effectively.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/2-get-started-with-real-time-dashboards"
            },
            {
                "question": "Which authorization scheme allows the dashboard to access data using the identity of the user who created the dashboard?",
                "options": [
                    "Pass-through identity",
                    "Dashboard editor's identity",
                    "User-specific identity",
                    "Admin identity"
                ],
                "correctAnswer": 1,
                "explanation": "The 'Dashboard editor's identity' scheme uses the identity of the user who created the dashboard to access data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/2-get-started-with-real-time-dashboards"
            },
            {
                "question": "What is the purpose of defining a base query in a real-time dashboard?",
                "options": [
                    "To retrieve a general set of records relevant for multiple tiles",
                    "To create a static dashboard without any data updates",
                    "To limit the number of tiles on the dashboard",
                    "To enhance the visual appeal of the dashboard"
                ],
                "correctAnswer": 0,
                "explanation": "A base query allows for the retrieval of a general set of records that can be used across multiple tiles, making the dashboard more maintainable.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/3-advanced-features"
            },
            {
                "question": "How can parameters enhance a real-time dashboard?",
                "options": [
                    "By allowing users to filter data displayed in the tiles",
                    "By automatically refreshing the dashboard every minute",
                    "By limiting the number of pages in the dashboard",
                    "By providing a static view of the data"
                ],
                "correctAnswer": 0,
                "explanation": "Parameters provide flexibility by enabling users to filter the data displayed in the tiles based on their selections.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/3-advanced-features"
            },
            {
                "question": "What does the 'auto refresh' feature do in a real-time dashboard?",
                "options": [
                    "It automatically updates dashboard data without manual intervention",
                    "It prevents any changes to the dashboard layout",
                    "It allows users to set a maximum refresh rate",
                    "It disables all other dashboard features"
                ],
                "correctAnswer": 0,
                "explanation": "The auto refresh feature ensures that the dashboard data is updated automatically, eliminating the need for manual refresh actions.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/3-advanced-features"
            },
            {
                "question": "What is a key principle to follow when designing real-time dashboards in Microsoft Fabric?",
                "options": [
                    "Complexity and Detail",
                    "Clarity and Simplicity",
                    "High Refresh Rates",
                    "Limited Interactivity"
                ],
                "correctAnswer": 1,
                "explanation": "Clarity and simplicity are essential to ensure that dashboards are easy to understand and use, avoiding clutter.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/create-real-time-dashboards-microsoft-fabric/4-real-time-dashboards-best-practices"
            }
        ]
    },
    {
        "category": "Implement a Data Warehouse with Microsoft Fabric",
        "questions": [
            {
                "question": "Which schema design is characterized by a fact table directly related to dimension tables?",
                "options": [
                    "Snowflake schema",
                    "Star schema",
                    "Galaxy schema",
                    "Hybrid schema"
                ],
                "correctAnswer": 1,
                "explanation": "The star schema is defined by its structure where a central fact table is directly connected to multiple dimension tables, facilitating efficient queries.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/2-understand-data-warehouse"
            },
            {
                "question": "What is the role of surrogate keys in dimension tables?",
                "options": [
                    "To provide a natural identifier from the source system",
                    "To uniquely identify each row in the dimension table",
                    "To track changes in dimension attributes over time",
                    "To aggregate data over temporal intervals"
                ],
                "correctAnswer": 1,
                "explanation": "Surrogate keys serve as unique identifiers for each row in a dimension table, ensuring consistency and accuracy within the data warehouse.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/2-understand-data-warehouse"
            },
            {
                "question": "Which of the following is a benefit of using zero-copy table clones in a data warehouse?",
                "options": [
                    "Increased storage costs",
                    "Faster data ingestion",
                    "Minimal storage costs while referencing the same data",
                    "Automatic data cleansing"
                ],
                "correctAnswer": 2,
                "explanation": "Zero-copy table clones allow for minimal storage costs because they reference the same underlying data files without duplicating them.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/3-understand-data-warehouse-fabric"
            },
            {
                "question": "What is the purpose of a semantic model in a data warehouse?",
                "options": [
                    "To define relationships and calculations for data insights",
                    "To store raw data without any transformations",
                    "To visualize data without any reporting tools",
                    "To manage user permissions in the data warehouse"
                ],
                "correctAnswer": 0,
                "explanation": "A semantic model is designed to define relationships between tables, aggregation rules, and calculations for deriving insights from data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/5-model-data"
            },
            {
                "question": "Which dynamic management view (DMV) would you use to get information about active requests in a session?",
                "options": [
                    "sys.dm_exec_connections",
                    "sys.dm_exec_sessions",
                    "sys.dm_exec_requests",
                    "sys.dm_exec_queries"
                ],
                "correctAnswer": 2,
                "explanation": "The sys.dm_exec_requests DMV provides details about each active request in a session, allowing for monitoring of ongoing operations.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/6-security-monitor"
            },
            {
                "question": "What permission must a user have at a minimum to connect to the SQL analytics endpoint?",
                "options": [
                    "ReadData",
                    "ReadAll",
                    "Read",
                    "Write"
                ],
                "correctAnswer": 2,
                "explanation": "The Read permission is essential for establishing a connection to the SQL analytics endpoint, as it allows the user to connect using the SQL connection string.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/6-security-monitor"
            },
            {
                "question": "Which type of slowly changing dimension (SCD) keeps full history for a given natural key?",
                "options": [
                    "Type 0 SCD",
                    "Type 1 SCD",
                    "Type 2 SCD",
                    "Type 3 SCD"
                ],
                "correctAnswer": 2,
                "explanation": "Type 2 SCD adds new records for changes and keeps full history for a given natural key, allowing for historical analysis.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/2-explore-data-load-strategies"
            },
            {
                "question": "What is the purpose of the REJECTED_ROW_LOCATION option in the COPY statement?",
                "options": [
                    "To specify the format of the source file",
                    "To store rejected rows separately",
                    "To skip header rows",
                    "To define the target table"
                ],
                "correctAnswer": 1,
                "explanation": "The REJECTED_ROW_LOCATION option allows for better error handling by storing rows that were not successfully imported.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/4-load-data-using-tsql"
            },
            {
                "question": "Which SQL operation is used to insert data from one table into another without creating a new table?",
                "options": [
                    "CREATE TABLE AS SELECT",
                    "COPY INTO",
                    "INSERT...SELECT",
                    "BULK INSERT"
                ],
                "correctAnswer": 2,
                "explanation": "The INSERT...SELECT operation is used to insert data from one table into another without creating a new table.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/4-load-data-using-tsql"
            },
            {
                "question": "Which feature allows combining data from a warehouse and a lakehouse in Microsoft Fabric?",
                "options": [
                    "COPY statement",
                    "Three-part naming convention",
                    "Shared Access Signature",
                    "Storage Account Key"
                ],
                "correctAnswer": 1,
                "explanation": "The three-part naming convention allows combining data from a warehouse and a lakehouse by referencing tables across these assets.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/4-load-data-using-tsql"
            },
            {
                "question": "Which T-SQL function is used to retrieve an approximate count of distinct values in a data warehouse?",
                "options": [
                    "COUNT",
                    "APPROX_COUNT_DISTINCT",
                    "DISTINCT_COUNT",
                    "ESTIMATE_COUNT"
                ],
                "correctAnswer": 1,
                "explanation": "The APPROX_COUNT_DISTINCT function is specifically designed to retrieve an approximate count of distinct values using the HyperLogLog algorithm, which is useful for large datasets where an exact count is not required.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-warehouse-microsoft-fabric/2-query-data"
            },
            {
                "question": "Which T-SQL ranking function assigns the same rank to rows with the same values but does not skip subsequent ranking positions?",
                "options": [
                    "ROW_NUMBER",
                    "RANK",
                    "DENSE_RANK",
                    "NTILE"
                ],
                "correctAnswer": 2,
                "explanation": "The DENSE_RANK function assigns the same rank to rows with the same values and does not skip subsequent ranking positions, unlike RANK, which does skip positions after ties.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/query-data-warehouse-microsoft-fabric/2-query-data"
            },
            {
                "question": "What does throttling in Microsoft Fabric indicate?",
                "options": [
                    "The system is running at optimal capacity",
                    "The processes require more capacity than is available",
                    "The data warehouse is being migrated to a new region",
                    "The license has expired and needs renewal"
                ],
                "correctAnswer": 1,
                "explanation": "Throttling in Microsoft Fabric indicates that the processes require more capacity than is available within the constraints of the purchased capacity license.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-data-warehouse/02-capacity-metrics"
            },
            {
                "question": "What does the sys.dm_exec_connections DMV return information about?",
                "options": [
                    "Active requests",
                    "Data warehouse connections",
                    "Authenticated sessions",
                    "Database transactions"
                ],
                "correctAnswer": 1,
                "explanation": "The sys.dm_exec_connections DMV specifically provides information regarding the connections to the data warehouse.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-data-warehouse/03-dynamic-management-views"
            },
            {
                "question": "Which queryinsights view directly provides the median execution time for SQL commands?",
                "options": [
                    "queryinsights.exec_requests_history",
                    "queryinsights.frequently_run_queries",
                    "queryinsights.long_running_queries",
                    "A calculated field derived from queryinsights.exec_requests_history only"
                ],
                "correctAnswer": 2,
                "explanation": "The queryinsights.long_running_queries view is specifically designed to provide aggregated data regarding query execution time, including the median execution time (median_total_elapsed_time_ms).",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-data-warehouse/04-query-insights"
            },
            {
                "question": "What is the primary benefit of Dynamic Data Masking (DDM)?",
                "options": [
                    "It permanently alters the data in the database",
                    "It allows real-time masking of sensitive data",
                    "It requires complex coding to implement",
                    "It exposes all data to nonprivileged users"
                ],
                "correctAnswer": 1,
                "explanation": "The primary benefit of DDM is its ability to mask sensitive data in real time, ensuring that unauthorized users do not see the actual data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-warehouse-in-microsoft-fabric/2-explore-dynamic-data-masking"
            },
            {
                "question": "Which masking function would you use to partially hide an email address while exposing the first letter?",
                "options": [
                    "default()",
                    "email()",
                    "partial(prefix_padding, padding_string, suffix_padding)",
                    "random(low, high)"
                ],
                "correctAnswer": 1,
                "explanation": "The email() function is specifically designed to expose the first letter of an email address while masking the rest.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-warehouse-in-microsoft-fabric/2-explore-dynamic-data-masking"
            },
            {
                "question": "You need to dynamically mask the PhoneNumber column to display only the last four digits, replacing the rest with XXX-XXX-. Which SQL command achieves this?",
                "options": [
                    "ALTER TABLE Customers ALTER COLUMN PhoneNumber ADD MASKED WITH (FUNCTION = 'random(1000000000,9999999999)')",
                    "ALTER TABLE Customers ALTER COLUMN PhoneNumber ADD MASKED WITH (FUNCTION = 'partial(0,\"XXX-XXX-\",4)')",
                    "ALTER TABLE Customers ALTER COLUMN PhoneNumber ADD MASKED WITH (FUNCTION = 'email()')",
                    "ALTER TABLE Customers ALTER COLUMN PhoneNumber ADD MASKED WITH (FUNCTION = 'default()')"
                ],
                "correctAnswer": 1,
                "explanation": "The correct command to apply a masking rule to the PhoneNumber column is to use the partial() function with the specified parameters.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-warehouse-in-microsoft-fabric/2-explore-dynamic-data-masking"
            },
            {
                "question": "What is the primary purpose of column-level security (CLS) in a data warehouse?",
                "options": [
                    "To enhance performance of queries",
                    "To restrict access to sensitive data",
                    "To simplify database management",
                    "To allow all users to access all data"
                ],
                "correctAnswer": 1,
                "explanation": "Column-level security is designed to restrict access to sensitive data, ensuring that only authorized users can view specific columns.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-warehouse-in-microsoft-fabric/4-implement-column-level-security"
            },
            {
                "question": "What is a key advantage of using column-level security compared to views?",
                "options": [
                    "More flexible in defining permissions",
                    "Automatically adapts to table structure changes",
                    "Can provide row-level security",
                    "Requires less maintenance"
                ],
                "correctAnswer": 1,
                "explanation": "Column-level security automatically adapts to changes in table structure, making it easier to manage than views which may require updates when the underlying structure changes.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-warehouse-in-microsoft-fabric/4-implement-column-level-security"
            }
        ]
    },
    {
        "category": "Manage a Microsoft Fabric environment",
        "questions": [
            {
                "question": "What role do deployment pipelines play in the CI/CD process within Fabric?",
                "options": [
                    "They automate the integration of code changes",
                    "They allow for the promotion of code changes to different environments",
                    "They manage version control for individual developers",
                    "They provide a platform for manual testing of code"
                ],
                "correctAnswer": 1,
                "explanation": "Deployment pipelines facilitate the promotion of code changes through various environments, ensuring a structured deployment process.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/implement-cicd-in-fabric/2-understand-cicd"
            },
            {
                "question": "Which of the following statements best describes continuous delivery?",
                "options": [
                    "It automatically releases updates into production without any testing",
                    "It occurs after continuous integration and involves deploying code to a staging environment for further testing",
                    "It is the process of merging code changes from multiple developers into a single branch",
                    "It focuses solely on the management of version control using Git"
                ],
                "correctAnswer": 1,
                "explanation": "Continuous delivery follows continuous integration and involves deploying code to a staging environment for additional automated testing before production release.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/implement-cicd-in-fabric/2-understand-cicd"
            },
            {
                "question": "What is the primary purpose of deployment pipelines in Microsoft Fabric?",
                "options": [
                    "To create user interfaces for applications",
                    "To automate the movement of content through development stages",
                    "To manage user permissions across environments",
                    "To store data securely in the cloud"
                ],
                "correctAnswer": 1,
                "explanation": "Deployment pipelines are designed to automate the movement of content through various stages of the development lifecycle, ensuring efficient updates and testing.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/implement-cicd-in-fabric/4-implement-deployment-pipelines"
            },
            {
                "question": "What is the primary purpose of monitoring in Microsoft Fabric?",
                "options": [
                    "To enhance user interface design",
                    "To collect system data and metrics for health assessment",
                    "To automate data ingestion processes",
                    "To create visual representations of data models"
                ],
                "correctAnswer": 1,
                "explanation": "Monitoring is essential for collecting data and metrics that help determine the health and operational status of a system.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-items/2-understand-monitoring"
            },
            {
                "question": "What is the primary function of the Monitor hub in Microsoft Fabric?",
                "options": [
                    "To create new data pipelines",
                    "To visualize and monitor Fabric activities",
                    "To store data permanently",
                    "To execute Spark jobs"
                ],
                "correctAnswer": 1,
                "explanation": "The Monitor hub is designed specifically to visualize and monitor various activities within Microsoft Fabric, making it easier to track performance and issues.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-items/3-use-monitor-hub"
            },
            {
                "question": "What is the primary function of Activator in Microsoft Fabric?",
                "options": [
                    "To store large volumes of data",
                    "To automate actions based on events",
                    "To visualize data in real-time dashboards",
                    "To manage user access and permissions"
                ],
                "correctAnswer": 1,
                "explanation": "Activator is designed to automate actions triggered by specific events in data streams.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/monitor-fabric-items/4-take-action-with-activator"
            },
            {
                "question": "In Fabric, what is the purpose of workspace roles?",
                "options": [
                    "To authenticate users via Microsoft Entra ID",
                    "To distribute ownership and access policies within a workspace",
                    "To apply granular permissions within a specific compute engine",
                    "To restrict access to specific files or folders in OneLake"
                ],
                "correctAnswer": 1,
                "explanation": "Workspace roles in Fabric are used to distribute ownership and access policies within a workspace, enabling control over who can access and manage resources.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/2-understand-fabric-security-model"
            },
            {
                "question": "What feature allows access to data in the lakehouse to be restricted to specific files or folders?",
                "options": [
                    "Workspace roles",
                    "Item permissions",
                    "OneLake data access controls",
                    "Granular engine permissions"
                ],
                "correctAnswer": 2,
                "explanation": "OneLake data access controls enable the restriction of access to specific files or folders within the lakehouse.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/2-understand-fabric-security-model"
            },
            {
                "question": "What role should be assigned to a data engineer who needs to create Fabric items and read data in a lakehouse?",
                "options": [
                    "Admin",
                    "Member",
                    "Contributor",
                    "Viewer"
                ],
                "correctAnswer": 2,
                "explanation": "The Contributor role allows users to create Fabric items and modify content, which meets the requirements for the data engineer.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/3-configure-workspace-and-item-permissions"
            },
            {
                "question": "What command is used to grant permissions to SQL objects using the SQL analytics endpoint?",
                "options": [
                    "ALLOW",
                    "GRANT",
                    "PERMIT",
                    "ENABLE"
                ],
                "correctAnswer": 1,
                "explanation": "The GRANT command is specifically used in SQL to provide permissions to users or roles for accessing database objects.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/3-configure-workspace-and-item-permissions"
            },
            {
                "question": "A data engineer needs access to only ONE lakehouse in a Fabric workspace. What's the MOST secure access method?",
                "options": [
                    "Workspace \"Viewer\" role.",
                    "Workspace \"Contributor\" role",
                    "Item permissions only",
                    "Workspace \"Admin\" role"
                ],
                "correctAnswer": 2,
                "explanation": "Granting item permissions directly on the lakehouse, without assigning any workspace role, adheres to the principle of least privilege.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/3-configure-workspace-and-item-permissions"
            },
            {
                "question": "Which T-SQL commands are used to apply granular permissions in a lakehouse?",
                "options": [
                    "CREATE, ALTER, DROP",
                    "GRANT, DENY, REVOKE",
                    "SELECT, INSERT, UPDATE",
                    "EXEC, CALL, DECLARE"
                ],
                "correctAnswer": 1,
                "explanation": "Granular permissions in a lakehouse are applied using T-SQL Data Control Language (DCL) commands such as GRANT, DENY, and REVOKE.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/secure-data-access-in-fabric/3-configure-workspace-and-item-permissions"
            },
            {
                "question": "What is OneLake in Microsoft Fabric?",
                "options": [
                    "A type of data warehouse",
                    "A hierarchical storage system built on Azure Data Lake Storage",
                    "A collection of workspaces",
                    "A dedicated resource for data science"
                ],
                "correctAnswer": 1,
                "explanation": "OneLake serves as a hierarchical storage system that simplifies data management across an organization, built on Azure Data Lake Storage architecture.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/2-fabric-architecture"
            },
            {
                "question": "What is the role of a domain in Microsoft Fabric?",
                "options": [
                    "To define the capacity available for executing workloads",
                    "To act as a container for items such as data warehouses and reports",
                    "To logically group workspaces for organizational purposes",
                    "To provide a single-pane-of-glass file-system namespace"
                ],
                "correctAnswer": 2,
                "explanation": "A domain is a logical grouping of workspaces used to organize items in a way that makes sense for an organization, such as grouping by sales, marketing, or finance.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/2-fabric-architecture"
            },
            {
                "question": "What is the primary function of a workspace in Microsoft Fabric?",
                "options": [
                    "To provide a hierarchical file-system namespace",
                    "To act as a container for items and manage access controls",
                    "To define the capacity available for executing workloads",
                    "To logically group workspaces for organizational purposes"
                ],
                "correctAnswer": 1,
                "explanation": "A workspace in Fabric acts as a container for items such as data warehouses, datasets, and reports, and provides controls for who can access these items.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/2-fabric-architecture"
            },
            {
                "question": "What is the primary tool used by Fabric admins to manage the platform?",
                "options": [
                    "Microsoft 365 admin center",
                    "Fabric admin portal",
                    "PowerShell cmdlets",
                    "Admin monitoring workspace"
                ],
                "correctAnswer": 1,
                "explanation": "The Fabric admin portal is specifically designed for managing all aspects of the Fabric platform.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/3-admin-role-tools"
            },
            {
                "question": "Where is license management for Fabric handled?",
                "options": [
                    "In the Azure portal",
                    "In the Microsoft 365 admin center",
                    "In Power BI service",
                    "In the Fabric management console"
                ],
                "correctAnswer": 1,
                "explanation": "License management for Fabric is specifically handled in the Microsoft 365 admin center, which is designed for managing user licenses and access.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/4-manage-security"
            },
            {
                "question": "What is the first step in securing data when managing sharing and distribution of items?",
                "options": [
                    "Implement sensitivity labels",
                    "Conduct regular audits",
                    "Granting the least permissive rights",
                    "Enable multi-factor authentication"
                ],
                "correctAnswer": 2,
                "explanation": "The first step in securing data is to grant the least permissive rights, which helps to minimize access and protect sensitive information.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/4-manage-security"
            },
            {
                "question": "What does the scanner API in Fabric allow admins to do?",
                "options": [
                    "Create new data warehouses",
                    "Scan Fabric items for sensitive data",
                    "Delete sensitive data from Fabric",
                    "Promote content across the organization"
                ],
                "correctAnswer": 1,
                "explanation": "The scanner API is specifically designed to enable admins to scan various Fabric items for sensitive data, enhancing data governance.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/5-govern-fabric"
            },
            {
                "question": "What is the primary purpose of data lineage in Microsoft Fabric?",
                "options": [
                    "To endorse Fabric items as trusted",
                    "To scan for sensitive data in Fabric items",
                    "To track the flow of data through Fabric",
                    "To promote content across the organization"
                ],
                "correctAnswer": 2,
                "explanation": "Data lineage allows you to track the flow of data through Fabric, including its origin, transformations, and destinations, providing insights into how data is used.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/administer-fabric/5-govern-fabric"
            }
        ]
    }
]

# Store quiz data in a cache to avoid large session cookies
quiz_cache = {}


@app.route('/')
def index():
    """Render the homepage with category selection"""
    categories = [category['category'] for category in QUIZ_DATA]
    # Clear any existing quiz session data
    for key in ['quiz_id', 'current_question', 'score']:
        if key in session:
            session.pop(key)
    return render_template('index.html', categories=categories)


@app.route('/quiz/<category>')
def quiz(category):
    """Render the quiz page for a specific category"""
    # Find the category data
    category_data = None
    for cat in QUIZ_DATA:
        if cat['category'] == category:
            category_data = cat
            break

    if category_data is None:
        return "Category not found", 404

    # Create a quiz ID and store data in cache instead of session
    quiz_id = str(random.randint(10000, 99999))
    quiz_cache[quiz_id] = {
        'category': category,
        'questions': category_data['questions'],
        'current_question': 0,
        'score': 0,
        'answers': []  # To store user's answers
    }

    # Store only the quiz ID in session
    session['quiz_id'] = quiz_id

    return render_template('quiz.html', category=category)


@app.route('/get_question', methods=['GET'])
def get_question():
    """API endpoint to get the current question"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        return jsonify({"error": "No active quiz"}), 400

    quiz_data = quiz_cache[quiz_id]

    if quiz_data['current_question'] >= len(quiz_data['questions']):
        return jsonify({"complete": True})

    # Get current question
    question_data = quiz_data['questions'][quiz_data['current_question']]
    # Don't send the correct answer to the client
    question_to_send = {
        "question": question_data["question"],
        "options": question_data["options"],
        "questionNumber": quiz_data['current_question'] + 1,
        "totalQuestions": len(quiz_data['questions'])
    }

    return jsonify(question_to_send)


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """API endpoint to submit an answer and get feedback"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        return jsonify({"error": "No active quiz"}), 400

    quiz_data = quiz_cache[quiz_id]
    data = request.get_json()
    selected_option = data.get('answer')

    current_q_index = quiz_data['current_question']
    question_data = quiz_data['questions'][current_q_index]

    is_correct = selected_option == question_data["correctAnswer"]
    if is_correct:
        quiz_data['score'] += 1

    # Save the answer
    quiz_data['answers'].append({
        'question': question_data['question'],
        'selected': selected_option,
        'correct': is_correct,
        'correctAnswer': question_data['correctAnswer']
    })

    # Move to next question
    quiz_data['current_question'] += 1

    # Prepare response
    response = {
        "correct": is_correct,
        "correctAnswer": question_data["correctAnswer"],
        "explanation": question_data["explanation"],
        "sourceUrl": question_data["sourceUrl"],
        "nextQuestion": quiz_data['current_question'] < len(quiz_data['questions']),
        "score": quiz_data['score'],
        "totalQuestions": len(quiz_data['questions'])
    }

    return jsonify(response)


@app.route('/results')
def results():
    """Show quiz results"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        # Redirect to home if no valid quiz
        return redirect(url_for('index'))

    quiz_data = quiz_cache[quiz_id]

    # Only show results if all questions have been answered
    if quiz_data['current_question'] < len(quiz_data['questions']):
        return redirect(url_for('quiz', category=quiz_data['category']))

    results_data = {
        "score": quiz_data['score'],
        "totalQuestions": len(quiz_data['questions']),
        "percentage": (quiz_data['score'] / len(quiz_data['questions'])) * 100,
        "category": quiz_data['category'],
        "answers": quiz_data['answers'],
        "questions": quiz_data['questions']
    }

    return render_template('results.html', results=results_data)


@app.route('/clear_quiz')
def clear_quiz():
    """Clear quiz data when starting a new quiz"""
    quiz_id = session.get('quiz_id')
    if quiz_id and quiz_id in quiz_cache:
        del quiz_cache[quiz_id]
    if 'quiz_id' in session:
        session.pop('quiz_id')
    return redirect(url_for('index'))


# Cleanup old quiz cache entries (would be called periodically in production)
def cleanup_quiz_cache():
    # Remove quizzes older than X time
    pass


if __name__ == '__main__':
    app.run(debug=True)