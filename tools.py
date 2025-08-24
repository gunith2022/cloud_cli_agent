from portia import tool


@tool
def get_user_input(required_fields: dict) -> dict:
    """
    Prompts the user for specific information based on a dictionary of requirements
    and returns the collected input.
    
    Args:
        required_fields: A dictionary where keys are field names and values are
                         prompts for the user.
                         
    Returns:
        A dictionary of the collected user input.
    """
    collected_data = []
    print("\nI need a few more details to help you with that:")
    for field_name, prompt in required_fields.items():
        user_input = input(f"    - {prompt} > ")
        collected_data.append(user_input)
    
    return collected_data

@tool
def display(command: str,message:str) -> str:
    """
    Displays the generated command to the user.
    
    Args:
        command: The command string to be displayed.
        message : Informational message to be displayed before the command.
                         
    Returns:
        A confirmation message.
    """
    print("\n:",message)
    print(f"    {command}\n")
    return "Command displayed successfully."



@tool
def commmand_run(command: str) -> str:
    """
    Executes the provided gcloud command and returns the output.
    
    Args:
        command: The command string to be executed (may include formatting).
                         
    Returns:
        The output of the executed command.
    """
    import subprocess
    import re

    try:
        # Remove markdown formatting like bash ... 
        clean_cmd = re.sub(r"```(?:bash)?", "", command).strip()

        # Ensure command starts from first 'gcloud'
        if "gcloud" in clean_cmd:
            clean_cmd = clean_cmd[clean_cmd.index("gcloud"):]
        else:
            return "Error: Command does not contain 'gcloud'."

        # Execute command
        result = subprocess.run(
            clean_cmd, shell=True, check=True,
            capture_output=True, text=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr.strip()}"