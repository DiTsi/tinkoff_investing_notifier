FROM python:3.9-slim
RUN useradd -d /app -s /bin/bash -u 10432 -g users investing
WORKDIR /app
COPY . .
RUN chown -R investing:users ./

USER investing
RUN pip install -r requirements.txt --no-warn-script-location
RUN cp config.yml.default config.yml

CMD ["python", "tinkoff.py"]
