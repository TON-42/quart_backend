# Use Alpine Linux as a base image
FROM alpine:3.20

# Install necessary dependencies to build Python
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    zlib-dev \
    bzip2-dev \
    readline-dev \
    sqlite-dev \
    ncurses-dev \
    gdbm-dev \
    xz-dev \
    linux-headers \
    tk-dev \
    libxml2-dev \
    libxslt-dev \
    curl \
    wget \
    tar \
    coreutils \
    ca-certificates

# Set environment variables for Python
ENV PYTHON_VERSION=3.12.0
ENV PYTHON_PIP_VERSION=24.0

# Download and install Python
RUN wget -O python.tar.xz https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz && \
    tar -xJf python.tar.xz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations --enable-shared --with-ensurepip=install && \
    make -j$(getconf _NPROCESSORS_ONLN) && \
    make install && \
    rm -rf /Python-${PYTHON_VERSION} && \
    rm -f /python.tar.xz

# Install pip
RUN wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    pip install --upgrade pip==${PYTHON_PIP_VERSION}

# Install components for the app
RUN pip3 install --no-cache-dir \
    aiofiles==23.2.1 \
    APScheduler==3.6.3 \
    blinker==1.8.2 \
    cachetools==4.2.2 \
    certifi==2024.6.2 \
    charset-normalizer==3.3.2 \
    click==8.1.7 \
    exceptiongroup==1.2.1 \
    gunicorn==22.0.0 \
    h11==0.14.0 \
    h2==4.1.0 \
    hpack==4.0.0 \
    Hypercorn==0.17.3 \
    hyperframe==6.0.1 \
    idna==3.7 \
    itsdangerous==2.2.0 \
    Jinja2==3.1.4 \
    MarkupSafe==2.1.5 \
    priority==2.0.0 \
    pyaes==1.6.1 \
    pyasn1==0.6.0 \
    python-dotenv==0.19.2 \
    python-telegram-bot==13.7 \
    pytz==2024.1 \
    Quart==0.19.6 \
    quart-cors==0.7.0 \
    requests==2.32.3 \
    rsa==4.9 \
    six==1.16.0 \
    taskgroup==0.0.0a4 \
    Telethon==1.35.0 \
    tomli==2.0.1 \
    tornado==6.4.1 \
    typing_extensions==4.12.2 \
    tzlocal==5.2 \
    urllib3==1.26.18 \
    Werkzeug==3.0.3 \
    wsproto==1.2.0 \
    SQLAlchemy==2.0.12 \
    alembic==1.10.3 \
    asyncpg \
    httpx \
    psycopg2-binary \
    aiohttp \
    quart-jwt-extended \
    telebot


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

EXPOSE 8080

# Command to run your application
CMD [ "python3", "main.py" ]