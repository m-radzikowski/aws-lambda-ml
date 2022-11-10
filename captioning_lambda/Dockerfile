FROM public.ecr.aws/docker/library/python:3.9.15-slim-bullseye AS build

WORKDIR /root

RUN apt-get update && apt-get install -y \
    curl \
    git \
    git-lfs

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

RUN git lfs install
RUN git clone --depth=1 https://huggingface.co/nlpconnect/vit-gpt2-image-captioning
RUN rm -rf vit-gpt2-image-captioning/.git

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

########################################

FROM public.ecr.aws/lambda/python:3.9.2022.10.26.12

COPY --from=build /root/vit-gpt2-image-captioning ./vit-gpt2-image-captioning

COPY --from=build /root/requirements.txt ./
RUN pip3 install -r requirements.txt --target "$LAMBDA_RUNTIME_DIR"

COPY main.py ./

CMD ["main.handler"]
