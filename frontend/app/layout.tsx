import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'CardDAV Sync Admin',
  description: 'Admin panel for managing CardDAV synchronization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main>{children}</main>
        <footer className="bg-muted text-muted-foreground p-4 text-center">
          <p>&copy; 2023 CardDAV Sync Admin. All rights reserved.</p>
        </footer>
      </body>
    </html>
  )
}