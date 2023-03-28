import requests
import random
from loguru import logger 
from concurrent.futures import ThreadPoolExecutor
host = "http://localhost:8000"


def submit():
    url = host + "/api/v1/commit"
    with ThreadPoolExecutor(max_workers=100) as executor:
        tasks = []
        # params = []
        for i in range(100):
            data={
                "name": f"test_{i}",
                "stu_id": ("".join([str(random.randint(1,9)) for _ in range(11)])),
                "major": "test",
                "res": [1,2,3,4,5,6,7,8,9],
                "instructor":"foo",
                "detail_res":"".join([
                    str(random.randint(
                    0,1
                    ) )for _ in range(120)
                ])
            }
            logger.info(
                f"submit {i} {data['name']} {data['stu_id']}"

            )
            tasks.append(executor.submit(requests.post, url, json=data))
            # executor.submit(requests.post, url, json=data)

        for task in tasks:
            logger.info(task.result().json())




def main ():
    submit()


if __name__ =="__main__":
    main()