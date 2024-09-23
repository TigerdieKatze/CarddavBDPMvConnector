# CarddavBDPMvConnector Frontend

This is the frontend component of the CarddavBDPMvConnector project, providing an admin panel for managing the CardDAV synchronization process.

## Features

- 📊 Dashboard for viewing sync status and triggering manual syncs
- ⚙️ Configuration management for CardDAV sync settings
- 🎨 Modern, responsive UI built with Next.js and Tailwind CSS
- 🔒 Secure, locally-accessible admin interface

## Tech Stack

- [Next.js](https://nextjs.org/) - React framework for production
- [React](https://reactjs.org/) - JavaScript library for building user interfaces
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [Radix UI](https://www.radix-ui.com/) - Unstyled, accessible UI components
- [Lucide React](https://lucide.dev/) - Beautiful & consistent icon toolkit

## Prerequisites

- Node.js 18.17.0 or later
- npm or yarn

## Getting Started

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Run the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

- `app/`: Contains the main application code
  - `page.tsx`: The main dashboard component
  - `layout.tsx`: The root layout component
  - `globals.css`: Global styles
- `components/`: Reusable React components
  - `ui/`: UI components from shadcn/ui
- `lib/`: Utility functions
- `public/`: Static assets

## Customization

### Styling

This project uses Tailwind CSS for styling. You can customize the design by modifying the `tailwind.config.ts` file and the component-specific styles.

### Adding New Features

To add new features or pages:

1. Create a new component in the `components/` directory
2. Add a new route in the `app/` directory if needed
3. Update the main `page.tsx` file to include your new component

## Building for Production

To create an optimized production build:

```bash
npm run build
# or
yarn build
```

The build artifacts will be stored in the `.next/` directory.

## Deployment

This frontend is designed to be deployed alongside the backend using Docker. Refer to the main project README for full deployment instructions.

## Contributing

Contributions to improve the admin panel are welcome. Please ensure you follow the project's coding standards and submit a pull request for review.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.

---

For more information on using Next.js, check out the [Next.js documentation](https://nextjs.org/docs).