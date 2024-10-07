# Project Parry

# prereq
```
copy .env_template .env

add STARROCKS_HOST value
e.g STARROCKS_HOST="starrocks://{user}:{host}:{fe_port}/{database}"

add BROKER_URL value
e.g BROKER_URL="localhost:9092"

-- Assuming you are activating Python 3 venv
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
possible export to bash file to not have to need to do this everytime
```

# install + work in shell
```
poetry shell
poetry install
```

# Tooling

## Create Fake Data
```
python src/create_fake_kafka_events.py
```
This script will generate fresh data every time it is run. It will also delete the existing directory so be careful when running it multiple times. It creates an amount based on TOTAL_AMOUNT_OF_DATA_TO_GENERATE variable.

# Routine Load

## High Level Notes
- It is a batch load (see image; created at = time in DB, custom_data = request time).
  - This example is off a local execution, 1 partition, no replication, and no partial update handling.
- It is self managed within starrocks. 
- It has multiple status' such as RUNNING, PAUSED, NEEDS SCHEDULE, etc.
- It has a lot of underlying config, such as how many errors it will tolerate before it PAUSE's itself.

<img width="1286" alt="image" src="https://github.com/user-attachments/assets/c3b50e71-472d-48f0-a4d7-d1c086fb21d8">

## Getting started (starts up FE node / BE node / Kafka / Inits Kafka Topic)
```
docker compose up -d
```
This will create a `starrocks` directory. This will closely reflect what gets spun up in our Kubernetes pods. Here is where the logs of live. 

## Once stood up, in mysql editor / cli - create the table you want to dump into
```
mysql>

create table if not exists event_messages (
  org_id bigint,
  external_id varchar(128) NOT NULL,
  created_at datetime NOT NULL default current_timestamp,
  event_type varchar(128),
  event_subtype varchar(128),
  custom_data JSON
)
PRIMARY KEY (org_id, external_id)
DISTRIBUTED BY HASH (org_id, external_id)
PROPERTIES( "replication_num" = "1" ); # important only for local, to bypass need for 3 BE nodes

```

## Also in mysql editor / cli - create the routine load job
```
mysql>

CREATE ROUTINE LOAD heya.event_loading ON event_messages
COLUMNS(org_id, external_id, created_at=now(), event_type, event_subtype, custom_data) -- important if you do not specify, it assumes ALL columns
PROPERTIES
(
    "format" = "JSON",
    "jsonpaths" ="[\"$.body.org_id\",\"$.body.req_data.general_data.event_id\",\"$.body.req_data.general_data.event_type\",\"$.body.req_data.general_data.event_subtype\",\"$.body.req_data.custom_data\"]" -- this is what it's looking for on the JSON object itself
)
FROM KAFKA
(
    "kafka_broker_list" = "broker:9094",
    "kafka_topic" = "transactions",
    "kafka_partitions" = "0",
    "kafka_offsets" = "OFFSET_BEGINNING"
);
```
Some special notes about this job. 
- You can parse a JSON object with dot notation
- The `kafka_partitions` property should equal the number of partitions we set. 
- The `kafka offsets` must equal the length of partitions. You're declaring where to start for each of them. 

## see jobs currently running
```
mysql> show routine load;
```
`show routine load` is your friend. It has a column called `TrackingSQL` that will provide you with a query to debug with. 
  - `e.g select tracking_log from information_schema.load_tracking_logs where job_id=16162`

## Load in messages via producer script from kafka library

```
$KAFKA_LOCATION is just the location of a locally installed kafka binary 
I'm currently using 3.3.1
```

send json file into kafka (after I downloaded from S3 or generated fake data)
```
$KAFKA_LOCATION/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic transactions < src/data/txn_events/1/0b8c089b-eddf-4ec1-bbd4-7951fa8d6df7.json
```


## Publish to Kafka (from local)
```
python src/produce_events.py
```
By default, publishes data generated / downloaded earlier to `transactions` topic, I created already. You can alter the `PATH = 'src/data'` value in the script to control what org data you'll send. By default, it sends everything to kafka. 

As a part of the generated data I have a `"request_created": "2024-09-27 17:50:50.739765+00:00"` in the custom data that I compare with the `created_at` column to measure general ingestion performance. 

Dangerous, but I've also written up a bash line to iterate through the entire data directory and produce these to kafka (local or AWS). You can set bootstrap-server to your `AWS_BROKER_URL` to send up to AWS; assuming you're using the unauthenticated PLAINTEXT broker urls. This iterates through all the files in that org. It's pretty slow via bash. 
```
for FILE in src/data/txn_events/1/*; do $KAFKA_LOCATION/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic transactions < $FILE; done
```


# Other files

kafka/offset.json - used to delete from topic
```
# you'll want to get the active offset amount for the partition you're deleting from first
$KAFKA_LOCATION/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --all-groups

# you'll want to set the PARTITION/CURRENT-OFFSET in the kafka/offset,json
$KAFKA_LOCATION/kafka-delete-records.sh --bootstrap-server localhost:9092 --offset-json-file kafka/offset.json
```
I got a bad message stuck in there and just wanted to clear it out.
