import os
from dotenv import load_dotenv
from kafka import KafkaProducer
from glob import glob

load_dotenv()
KAFKA_SERVER = os.getenv('BROKER_URL')
PATH = 'src/data'

producer = KafkaProducer(
   bootstrap_servers=KAFKA_SERVER,
)

def _produce(obj):
   kafka_message = obj.encode("utf8")
   producer.send('transactions', kafka_message)
   producer.flush()

def produce_from_data_dir():
   files = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], '*.json'))]
   for file in files:
      f = open(file, "r")
      _produce(f.read())


if __name__ == '__main__':
   produce_from_data_dir()