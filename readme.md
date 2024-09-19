# CarddavBDPMvConnector

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
- [Dry Run Mode](#dry-run-mode)
- [Warnings](#warnings)
- [Risks](#risks)
- [TODO](#todo)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Overview

CarddavBDPMvConnector is an automated tool designed to synchronize member data between the Mitgliederverwaltung (MV) system and a CardDAV server for scout groups within the Bund der Pfadfinderinnen und Pfadfinder (BDP). This project streamlines the management of email distribution lists by automatically adding and updating member information based on their group assignments in the MV system.

## Features

- 🔄 Automated synchronization between MV and CardDAV server
- 👥 Support for group assignments (Sippen, Runden, and Meuten)
- 🕒 Daily scheduling option for regular updates
- 🧪 Dry run mode for testing without making changes
- 📧 Email notifications for important events (e.g., dangling contacts)

## Prerequisites

- Docker
- Access to a CardDAV server
- MV system credentials
- SMTP server for sending notifications

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CarddavBDPMvConnector.git
   cd CarddavBDPMvConnector
   ```

2. Build the Docker image:
   ```bash
   docker build -t carddav-sync .
   ```

## Usage

Run the Docker container with the following environment variables:

```bash
docker run -d \
  -e CARDDAV_URL=https://your-carddav-server.com/dav/ \
  -e USERNAME=your_carddav_username \
  -e PASSWORD=your_carddav_password \
  -e RUN_SCHEDULE=daily \
  -e NOTIFICATION_EMAIL=admin@example.com \
  -e SMTP_SERVER=smtp.example.com \
  -e SMTP_PORT=587 \
  -e SMTP_USERNAME=your_smtp_username \
  -e SMTP_PASSWORD=your_smtp_password \
  -e MV_USERNAME=your_mv_username \
  -e MV_PASSWORD=your_mv_password \
  -e DRY_RUN=False \
  -v /path/on/host:/app \
  carddav-sync
```

Replace the environment variables with your actual configuration.

## Configuration Options

| Variable | Description |
|----------|-------------|
| `CARDDAV_URL` | URL of your CardDAV server |
| `USERNAME` | CardDAV server username |
| `PASSWORD` | CardDAV server password |
| `RUN_SCHEDULE` | Set to "daily" for scheduled runs or "single" for one-time execution |
| `NOTIFICATION_EMAIL` | Email address for receiving notifications |
| `SMTP_SERVER` | SMTP server for sending notifications |
| `SMTP_PORT` | SMTP server port |
| `SMTP_USERNAME` | SMTP server username |
| `SMTP_PASSWORD` | SMTP server password |
| `MV_USERNAME` | Mitgliederverwaltung (MV) system username |
| `MV_PASSWORD` | Mitgliederverwaltung (MV) system password |
| `DRY_RUN` | Set to "True" for testing without making changes, "False" for normal operation |

## Dry Run Mode

To test the synchronization without making changes to your CardDAV server, set the `DRY_RUN` environment variable to "True". This will log all actions that would be taken without actually modifying any data.

## Warnings

⚠️ **Please read carefully before using:**

1. **Group Assignments**: Ensure that groups in the MV system are correctly assigned to Sippen, Runden, and Meuten. Incorrect assignments will lead to improper synchronization.

2. **Credential Security**: Handle all credentials (CardDAV, MV, SMTP) with utmost care. Never hardcode them in the script or expose them in public repositories.

3. **Regular Updates**: Keep all dependencies up-to-date to mitigate potential security vulnerabilities.

4. **Testing**: Always use the dry run mode to verify changes before applying them to your production environment.

5. **Data Backup**: Regularly backup your CardDAV data to prevent potential data loss during synchronization.

## Risks

🚨 **Be aware of the following risks:**

1. **Data Privacy**: This tool handles personal information. Ensure compliance with data protection regulations (e.g., GDPR) in your region.

2. **Data Integrity**: Synchronization errors could potentially lead to data inconsistencies between MV and CardDAV systems.

3. **System Downtime**: Failures in either the MV system or CardDAV server during synchronization could impact the process.

4. **Rate Limiting**: Frequent synchronization attempts might trigger rate limiting on the CardDAV server.

5. **Notification Reliability**: Ensure that the SMTP configuration is correct and stable to receive important notifications about the synchronization process.

## TODO

- [ ] Implement support for additional CardDAV servers
- [ ] Create a web interface for easier configuration and monitoring
- [ ] Enhance logging capabilities for better troubleshooting
- [ ] Implement multi-language support for notifications and logs
- [ ] Add unit and integration tests for improved reliability
- [ ] Create a backup and restore feature for CardDAV data
- [ ] Implement a conflict resolution mechanism for data discrepancies

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code adheres to the project's coding standards and include appropriate tests for new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:

1. Check the existing [issues](https://github.com/yourusername/CarddavBDPMvConnector/issues) in the GitHub repository
2. If your issue isn't addressed, open a new issue with a detailed description
3. For urgent matters, contact the maintainer directly at harry@wildgaense-leer.de

---

📋 **Note**: This README is a living document and will be updated as the project evolves. Always refer to the latest version for the most up-to-date information.