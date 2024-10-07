import os, json, shutil
from generator import transaction

ROOT_PATH = 'src/data'
GENERATED_PATH = f'{ROOT_PATH}/transactions'

TOTAL_AMOUNT_OF_DATA_TO_GENERATE = 100

 # threshold is the amount of data to generate, ratio'd to TOTAL_AMOUNT_OF_DATA_TO_GENERATE
 # e.g threshold: 2.4 = 2.4% of TOTAL_AMOUNT_OF_DATA_TO_GENERATE for department N
DEPARTMENTS = [
    { "department_id": 1, "threshold": 2.4 },
    { "department_id": 2, "threshold": 4.6 },
    { "department_id": 3, "threshold": 8 },
    { "department_id": 4, "threshold": 8.1 },
    { "department_id": 5, "threshold": 9.8 },
    { "department_id": 6, "threshold": 12.4 },
    { "department_id": 7, "threshold": 26.6 },
    { "department_id": 8, "threshold": 28.1 },
]

def _make_dir(path):
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)    


if __name__ == '__main__':

    if os.path.isdir(GENERATED_PATH):
        shutil.rmtree(GENERATED_PATH)
    _make_dir(GENERATED_PATH)

    for department in DEPARTMENTS:
        amount_generated = 0
        department_id = department["department_id"]
        threshold = (TOTAL_AMOUNT_OF_DATA_TO_GENERATE * department["threshold"]) / 100
        _make_dir(f'{GENERATED_PATH}/{department_id}')
        while (threshold > 0):
            event = transaction.construct(department_id)
            with open(f'{GENERATED_PATH}/{department_id}/{event["req_id"]}.json', 'w') as f:
                json.dump(event, f)
            threshold -= 1
