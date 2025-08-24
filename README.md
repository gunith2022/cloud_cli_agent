# Cloud CLI Agent

This project is an intelligent assistant designed to simplify cloud infrastructure management by translating natural language into executable command-line interface (CLI) commands.

***

## The Problem 🤔

In the current IT landscape, organizations invest significant resources to train their employees on the intricacies of cloud platforms like Google Cloud, AWS, and Azure. The alternative is to hire costly professionals with specialized knowledge. Managing cloud resources via the CLI requires a deep understanding of specific commands, flags, and syntax, creating a high barrier to entry and increasing operational overhead.

***

## Our Solution 💡

The Cloud CLI Agent is an intelligent assistant that bridges this gap. It empowers users to manage cloud infrastructure by translating simple, natural language prompts into accurate, executable `gcloud` commands.

* **Lowers the Technical Barrier**: It allows team members without deep CLI expertise to perform cloud operations confidently.
* **Increases Efficiency**: It automates the process of finding and constructing complex commands, saving time and reducing human error.
* **Reduces Costs**: By making cloud management more accessible, it reduces the need for extensive specialized training or hiring.
* **Future-Ready**: The long-term vision is to support all major cloud vendors, which will simplify multi-cloud management and reduce vendor lock-in.

***

## How It Works

The agent operates in a conversational loop, guided by a sophisticated system prompt that defines its role as a Google Cloud expert.

1.  **Understand the Task**: The agent parses the user's natural language request (e.g., "create a virtual machine in GCP").
2.  **Gather Information**: If the request lacks necessary details (like instance name, machine type, etc.), it uses the `get_user_input` tool to prompt the user for the missing information interactively.
3.  **Generate Command**: Once all details are collected, the agent constructs the precise `gcloud` command.
4.  **Display and Confirm**: The agent displays the generated command to the user for verification using the `display` tool. For critical commands, the `CLIExecutionHooks` in `main.py` ensures the user is asked for confirmation before proceeding.
5.  **Execute**: Upon user confirmation, the `commmand_run` tool executes the command in the shell, capturing and returning the output or any errors.

***

## Project Structure

```text
.
├── main.py             # Main application entry point, agent configuration, and system prompt
├── tools.py            # Custom tools for user interaction and command execution
├── requirements.txt    # Python package dependencies
└── .env.example        # Example file for environment variables
```

## Setup and Installation 🛠️

Follow these steps to set up and run the project locally.

***

### Prerequisites

Before running the application, you must have the following set up:

* **Google Cloud CLI**: The `gcloud` CLI must be installed on your system. You can find the installation instructions on the [official Google Cloud documentation](https://cloud.google.com/sdk/docs/install).
* **Google Cloud Project**: You need an active Google Cloud Project with its **Project ID**.
* **Billing Enabled**: The project must have **billing enabled** to allow the creation of resources that incur costs (e.g., virtual machines, storage buckets).
* **Authentication**: You must be authenticated with Google Cloud. Run the following commands to log in and set your default project:
    ```bash
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```
    Replace `YOUR_PROJECT_ID` with your actual Google Cloud Project ID.

***

### Application Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    Install the required packages from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a `.env` file by copying the `.env.example` file.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and add your Google API key:
    ```
    GOOGLE_API_KEY="your_google_api_key_here"
    ```

***

## Usage 🚀

Run the `main.py` script to start the agent.
```bash
python main.py
