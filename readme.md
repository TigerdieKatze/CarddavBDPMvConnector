# CarddavBDPMvConnector

This project was created to automate the email distribution lists in scout groups within the BDP. It automatically adds and manages new members from the MV. This project only works if the groups in the MV are correctly assigned -> Sippen, Runden, and Meuten.

## Table of Contents
- [Usage](#usage)
- [Dry Run Mode](#dry-run-mode)
- [Warnings](#warnings)
- [TODO](#todo)
- [Deployment](#deployment)
- [Risks](#risks)
- [Collaboration](#collaboration)

## Usage

To use this updated script:

1. Save the Python script as `carddav_sync.py`.
2. Update the `requirements.txt` file with the contents provided in this repository.
3. Build the Docker image:
    ```sh
    docker build -t carddav-sync .
    ```
4. Run the container with the desired configuration:
    ```sh
    docker run -e CARDDAV_URL=https://your-server.com/dav/ \
    -e USERNAME=your_username \
    -e PASSWORD=your_password \
    -e RUN_SCHEDULE=daily \
    -e NOTIFICATION_EMAIL=admin@example.com \
    -e SMTP_SERVER=smtp.example.com \
    -e SMTP_PORT=587 \
    -e SMTP_USERNAME=your_smtp_username \
    -e SMTP_PASSWORD=your_smtp_password \
    -e MV_USERNAME=your_mv_username \
    -e MV_PASSWORD=your_mv_password \
    -v /path/on/host:/app \
    carddav-sync
    ```

Make sure to replace the environment variables with your actual configuration. The `-v` option mounts a directory from the host to the container, allowing the state file to persist between runs.

## Dry Run Mode

A new dry run mode has been added to allow testing the script without making any changes to the CardDAV server. To use this mode:

1. Set the `DRY_RUN` environment variable to `"True"` when running the container:
    ```sh
    docker run -e DRY_RUN=True ... carddav-sync
    ```
2. In dry run mode, the script will log all actions it would take without actually modifying any data on the CardDAV server.
3. This is useful for testing configuration changes or verifying the script's behavior before applying changes to your production environment.

## Warnings

- Ensure that the groups in the MV are correctly assigned to Sippen, Runden, and Meuten.
- Handle your credentials securely and avoid hardcoding them in the script.
- Regularly update your dependencies to avoid security vulnerabilities.
- Use dry run mode to test changes before applying them to your production environment.

## TODO

- [ ] Add support for additional CardDAV servers.
- [ ] Implement a web interface for easier configuration.
- [ ] Add logging and monitoring features.
- [ ] Improve error handling and reporting.
- [ ] Enhance dry run mode with detailed reporting of potential changes.

## Deployment

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/CarddavMvConnector.git
    cd CarddavMvConnector
    ```
2. Build the Docker image:
    ```sh
    docker build -t carddav-sync .
    ```
3. Run the container with the desired configuration as described in the [Usage](#usage) section.

## Risks

- **Data Privacy**: Ensure that sensitive information such as usernames and passwords are handled securely.
- **Data Integrity**: Incorrect group assignments in the MV can lead to improper email distribution.
- **Dependency Management**: Outdated dependencies can introduce security vulnerabilities.
- **Dry Run Limitations**: While dry run mode helps prevent unintended changes, it may not catch all potential issues in a production environment.

## Collaboration

We welcome contributions! To collaborate:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push your branch to your fork.
4. Create a pull request with a detailed description of your changes.

For major changes, please open an issue first to discuss what you would like to change.