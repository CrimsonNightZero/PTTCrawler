FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ppt.py ./
COPY Module ./Module

CMD [ "python", "./ppt.py", "--board_url=https://www.ptt.cc/bbs/Gossiping/index.html", "--run_mode=1", "--start_index=30000", "--end_index=5", "--board=Gossiping", "--res_time=20"]
