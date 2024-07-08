# SIC-SOC-LLM

<p>
<img src="https://img.shields.io/badge/repo%20status-completed%20inactive-orange" class="img-fluid" alt="Repository status">
<img src="https://img.shields.io/badge/stability-experimental%20⚠️-red" class="img-fluid" alt="Code stability">
<img src="https://shields.io/badge/MacOS--9cf?logo=Apple&amp;style=social" class="img-fluid" alt="MacOS">
<a href="https://codecov.io/gh/datasciencecampus/sic-soc-llm-wip"> <img src="https://codecov.io/gh/datasciencecampus/sic-soc-llm-wip/graph/badge.svg?token=7AGC0OLJTX" class="img-fluid" alt="codecov"></a>
</p>


## Overview

This app/package has been created by the [Data Science Campus](https://datasciencecampus.ons.gov.uk/) as a proof of concept to evaluate Large Language Models (LLM) potential to assist
with classification coding. It uses the `LangChain` library to perform Retrieval Augmented Generation (RAG) based on the provided classification index. A special case of Standard Industrial Classification (SIC) coding has been used as the primary test case, see [method explanation](https://datasciencecampus.github.io/sic-soc-llm/method.html#method). An example deployment using `Streamlit` allows for interactive exploration of the model's capabilities.

## Data sources

Examples of simplified SIC, Standard Occupational Classification (SOC) and Classification of Individual Consumption According to Purpose (COICOP) are included in the `example_data` folder. These condensed indices are flattened subsets of more detailed indices officially published online, such as the [UK SIC 2007](https://www.ons.gov.uk/methodology/classificationsandstandards/ukstandardindustrialclassificationofeconomicactivities/uksic2007), [UK SOC 2020](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020), and [COICOP 2018 (pdf)](https://unstats.un.org/unsd/classifications/unsdclassifications/COICOP_2018_-_pre-edited_white_cover_version_-_2018-12-26.pdf).

> ⚠️ **Warning:** The example data is provided for demonstration purposes only. No guarrantee is given for its accuracy or up to date status.

In this project, we focused on the SIC. A flexible representation of this hierarchical index (including metadata) has been implemented within the `data_models` submodule, enabling enhanced context for RAG/LLM. This representation can be used independently for other SIC coding tasks or easily extended to accommodate different classification indices.

The SIC index hierarchy object is built using three data sources provided by ONS:

- [Published UK SIC summary of structure worksheet (xlsx)](https://www.ons.gov.uk/file?uri=/methodology/classificationsandstandards/ukstandardindustrialclassificationofeconomicactivities/uksic2007/publisheduksicsummaryofstructureworksheet.xlsx) - location needs to be specified in config

- [UK SIC2007 indexes with addendum December 2022 (xlsx)](https://www.ons.gov.uk/file?uri=/methodology/classificationsandstandards/ukstandardindustrialclassificationofeconomicactivities/uksic2007/uksic2007indexeswithaddendumdecember2022.xlsx) - location needs to be specified in config

- [SIC resource file by ONSdigital/dp-classification-tools (js)](https://github.com/ONSdigital/dp-classification-tools/blob/develop/standard-industrial-classification/data/sicDB.js) - included inside the package


## Installation

### 1. Virtual environment

It is recommended that you install the project with its required dependencies in a virtual environment.  When the virtual environment is activated, any subsequent Python commands will use the Python interpreter and libraries specific to that isolated environment. This ensures that the project uses the correct versions of the dependencies specified in its requirements.

Create and activate a new virtual environment on Linux/OS X:

```{shell}
python3.10 -m venv .venv
source .venv/bin/activate
```


### 2. Requirements
Update pip and install requirements:
```
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```
 The -e flag installs the project in "editable" mode, which means that any changes made to the project code will be reflected immediately without the need to reinstall. The ".[dev]" part specifies that both the regular requirements and the development requirements should be installed.

### 3. LLM authentication:

The package provides code to use popular LLMs, access to the LLMs is a perquisite for use. Depending on your choice, keys/credentials may need to be added, for example:

- Include a personal [OpenAI](https://openai.com/) API in .env as

```{shell}
OPENAI_API_KEY="<your key>"
```

- Authenticate for [Vertex AI](https://cloud.google.com/model-garden?hl=en):

```{shell}
gcloud config set project "<PROJECT_ID>"
gcloud auth application-default login
```




## Usage

Examples of how to use the `sic-soc-llm` package can be found in [Tutorials](https://datasciencecampus.github.io/sic-soc-llm/tutorials/) and [References](https://datasciencecampus.github.io/sic-soc-llm/reference/).

### Configuration

The `sic-soc-llm` package uses a configuration file in TOML format to specify the paths to the data files and the names of the models to use. An example configuration file is provided in `sic_soc_llm_config.toml` and is read by the [`get_config`](https://datasciencecampus.github.io/sic-soc-llm/reference/get_config.html) function. The following fields are required:

| Field | Type | Default value |
| --- | --- | --- |
[lookups]| | |
| sic_structure | str | "data/sic-index/publisheduksicsummaryofstructureworksheet.xlsx" |
| sic_index | str | "data/sic-index/uksic2007indexeswithaddendumdecember2022.xlsx" |
| sic_condensed | str | "sic_2d_condensed.txt" |
| soc_condensed | str | "soc_4d_condensed.txt" |
| coicop_condensed | str | "coicop_5d_condensed.txt" |
| [llm]| | |
| db_dir | str | "data/sic-index/db" |
| embedding_model_name | str | "all-MiniLM-L6-v2" |
| llm_model_name | str | "gemini-pro" |


Make sure to update the file paths and model names according to your specific setup. While the condensed indexes (`.txt`) are included in the package, the `.xlsx` files need to be downloaded from the ONS website (mentioned above) and placed in the specified locations.

### Run and deploy Streamlit app

To run the Streamlit app, use the following command:

```{shell}
streamlit run app/Welcome.py --server.port 8500
```

The app will be available at `http://localhost:8500/`.


Example commands used to build and deploy the app as a GCP Cloud Run service are provided in `cloud_deploy.sh` (which references `Dockerfile` and `app.yaml`). The `Dockerfile` contains a set of instructions for building a Docker image. It specifies the base image to use, the files and directories to include, the dependencies and the commands to run. The `app.yaml` file is used to specify the configuration of the Cloud Run service, including the container image to deploy, the service name, and the port to expose.


## Development and testing

### 1. Pre-commit actions

This repository contains a configuration of pre-commit hooks. If approaching this project as a developer, you are encouraged to install and enable `pre-commits` by running the following in your shell:

```
pip install pre-commit
pre-commit install
```

### 2. Unit tests

To run the unit tests, use the following command:

```{shell}
python -m pytest
```


### 3. Building documentation and webpage:


1. Build (Quatro markdown) `reference` files from docstrings:

```{shell}
cd docs
python -m quartodoc build
```

2. Render webpage from Quarto markdowns in `docs` dir (including `reference` files):

```{shell}
quarto render
```

## License
<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->
The code, unless otherwise stated, is released under [the MIT Licence][mit].
The documentation for this work is subject to [© 2024 Crown Copyright (Office for National Statistics)][copyright] and is available under the terms of the [Open Government 3.0][ogl] licence.

[mit]: https://github.com/datasciencecampus/sic-soc-llm?tab=MIT-1-ov-file
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

## Data Science Campus
At the [Data Science Campus](https://datasciencecampus.ons.gov.uk/about-us/) we apply data science, and build skills, for public good across the UK and internationally. Get in touch with the Campus at [datasciencecampus@ons.gov.uk](mailto:datasciencecampus@ons.gov.uk).
