# CarddavBDPMvConnector

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
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
- 🕒 Configurable sync schedule (daily, weekly, monthly)
- 🧪 Dry run mode for testing without making changes
- 📧 Email notifications for important events (e.g., dangling contacts)
- 🔧 Web-based admin panel for easy configuration and monitoring
- 🔒 API and admin panel accessible only from the local machine for enhanced security

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
   cp backend/config.json config/
   ```

3. Edit the `config/config.json` file with your actual configuration.

4. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```

## Project Structure

The project is now structured into backend and frontend components:

### Backend
- `main.py`: The entry point of the application, handling API routes and scheduling.
- `config.py`: Manages loading and saving of configuration.
- `models.py`: Contains data models used in the application.
- `carddav_sync.py`: Handles the core CardDAV synchronization logic.
- `mv_integration.py`: Manages integration with the MV system.
- `notifications.py`: Handles email notifications.

### Frontend
- Next.js application for the admin panel
- Tailwind CSS for styling
- React components for UI elements

## Usage

1. After starting the Docker containers, the services will be available at:
   - Backend API: `http://localhost:5000`
   - Frontend Admin Panel: `http://localhost:3000`

2. Access the admin panel by opening `http://localhost:3000` in your web browser.

3. Use the admin panel to:
   - View sync status
   - Trigger manual synchronization
   - Configure group mappings and other settings
   - Toggle dry run mode

4. The backend API endpoints (accessible only from the local machine):
   - Trigger sync: `POST /sync`
   - Check status: `GET /status`
   - Get configuration: `GET /config`
   - Update configuration: `POST /config`

## Configuration

You can update the following configuration options via the admin panel or API:

- Group Mappings
- Default Group
- Apply Group Mapping to Parents
- Apply Default Group to Parents
- Run Schedule
- Notification Email
- Dry Run Mode

## Security Note

The API and admin panel are intentionally configured to be accessible only from the machine running Docker. This prevents unauthorized access from external networks. If you need to access these services from another machine, you should use a secure method such as SSH tunneling.

## Dry Run Mode

To test the synchronization without making changes to your CardDAV server, enable the "Dry Run" option in the admin panel. This will log all actions that would be taken without actually modifying any data.

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