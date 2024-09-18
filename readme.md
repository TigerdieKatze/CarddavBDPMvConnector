# CarddavBDPMvConnector

This project was created to automate the email distribution lists in scout groups within the BDP. It automatically adds and manages new members from the MV. This project only works if the groups in the MV are correctly assigned -> Sippen, Runden, and Meuten.

## Table of Contents
- [Usage](#usage)
- [Warnings](#warnings)
- [TODO](#todo)
- [Deployment](#deployment)
- [Risks](#risks)
- [Collaboration](#collaboration)

## Usage

To use this updated script:

1. Save the Python script as `carddav_sync.py`.
2. Update the `requirements.txt` file with the contents provided above.
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
    -v /path/on/host:/app \
    carddav-sync
    ```

Make sure to replace the environment variables with your actual configuration. The `-v` option mounts a directory from the host to the container, allowing the state file to persist between runs.

## Warnings

- Ensure that the groups in the MV are correctly assigned to Sippen, Runden, and Meuten.
- Handle your credentials securely and avoid hardcoding them in the script.
- Regularly update your dependencies to avoid security vulnerabilities.

## TODO

- [ ] Add support for additional CardDAV servers.
- [ ] Implement a web interface for easier configuration.
- [ ] Add logging and monitoring features.
- [ ] Improve error handling and reporting.

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

## Collaboration

We welcome contributions! To collaborate:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push your branch to your fork.
4. Create a pull request with a detailed description of your changes.

For major changes, please open an issue first to discuss what you would like to change.