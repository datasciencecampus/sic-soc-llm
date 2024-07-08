FROM python:3.10.4-buster
ENV PYTHONUNBUFFERED True

# Copy app code
WORKDIR /sic-soc
COPY . ./
RUN ls -laRt

# Upgrade pip and install requirements
RUN python -m pip install --upgrade pip
RUN python -m pip install pysqlite3-binary
RUN python -m pip install -e ".[app]" --no-cache-dir

# Expose port you want your app on
ENV PORT=8080
ENV HOSTNAME="0.0.0.0"
EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

# Run
ENTRYPOINT ["streamlit", "run", "app/Welcome.py", "--server.port=8080", "--server.address=0.0.0.0"]
