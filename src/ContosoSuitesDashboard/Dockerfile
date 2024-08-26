FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
	build-essential \
	curl \
	software-properties-common \
	git \
	&& rm -rf /var/lib/apt/lists/*
COPY . /app
RUN pip3 install -r requirements.txt
# You must have a secrets.toml file in .streamlit.
# This file should contain the following sections and keys:
    # aoai: endpoint, key, deployment_name
    # search: endpoint, key, index_name
    # speech: key, region
EXPOSE 80
ENTRYPOINT ["streamlit", "run", "Index.py", "--server.port=80", "--server.address=0.0.0.0"]