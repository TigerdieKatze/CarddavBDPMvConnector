# CarddavBDPMvConnector

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Security Note](#security-note)
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
- 🔧 Configurable settings via API
- 🔒 API accessible only from the local machine for enhanced security

## Prerequisites

- Docker
- Docker Compose

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CarddavBDPMvConnector.git
   cd CarddavBDPMvConnector
   ```

2. Create a `config` directory and copy the default `config.json` file:
   ```bash
   mkdir config
   cp config.json config/
   ```

3. Edit the `config/config.json` file with your actual configuration.

## Usage

1. Start the Docker container:
   ```bash
   docker-compose up -d
   ```

2. The API will be available at `http://localhost:5000`, but only accessible from the machine running Docker. You can use the following endpoints:

   - Trigger sync: `POST /sync`
   - Check status: `GET /status`
   - Get configuration: `GET /config`
   - Update configuration: `POST /config`

   Example usage (from the machine running Docker):
   ```bash
   curl http://localhost:5000/status
   ```

## Configuration

You can update the following configuration options via the API:

- GROUP_MAPPING
- DEFAULT_GROUP
- APPLY_GROUP_MAPPING_TO_PARENTS
- APPLY_DEFAULT_GROUP_TO_PARENTS
- RUN_SCHEDULE
- NOTIFICATION_EMAIL
- DRY_RUN

Example of updating configuration (from the machine running Docker):

```bash
curl -X POST -H "Content-Type: application/json" -d '{"DEFAULT_GROUP": "New Default Group", "DRY_RUN": true}' http://localhost:5000/config
```

## Security Note

The API is intentionally configured to be accessible only from the machine running Docker. This prevents unauthorized access from external networks. If you need to access the API from another machine, you should use a secure method such as SSH tunneling.

## Dry Run Mode

To test the synchronization without making changes to your CardDAV server, set the `DRY_RUN` configuration option to `true`. This will log all actions that would be taken without actually modifying any data.

## Warnings

⚠️ **Please read carefully before using:**

1. **Group Assignments**: Ensure that groups in the MV system are correctly assigned to Sippen, Runden, and Meuten. Incorrect assignments will lead to improper synchronization.

2. **Credential Security**: Handle all credentials (CardDAV, MV, SMTP) with utmost care. Never expose them in public repositories.

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