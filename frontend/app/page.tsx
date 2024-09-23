'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Settings } from "lucide-react"
import { StatusCard } from '@/components/StatusCard'
import { GroupMappings } from '@/components/GroupMappings'
import { ConfigSettings } from '@/components/ConfigSettings'
import { Toast } from '@/components/Toast'

const API_BASE_URL = 'http://127.0.0.1:5000'

export default function Home() {
  const [status, setStatus] = useState<{ details: string, last_run: string, status: string } | null>(null)
  const [config, setConfig] = useState<Record<string, any> | null>(null)
  const [groupMappings, setGroupMappings] = useState<{ checkGroup: string; referenceGroup: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  useEffect(() => {
    fetchStatus()
    fetchConfig()
  }, [])

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`)
      const data = await response.json()
      setStatus(data)
    } catch (error) {
      console.error('Error fetching status:', error)
      showToast("Failed to fetch sync status", "error")
    }
  }

  const fetchConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/config`)
      const data = await response.json()
      setConfig(data)
      setGroupMappings(Object.entries(data.GROUP_MAPPING).map(([checkGroup, referenceGroup]) => ({
        checkGroup,
        referenceGroup: referenceGroup as string
      })))
      setLoading(false)
    } catch (error) {
      console.error('Error fetching config:', error)
      showToast("Failed to fetch configuration", "error")
      setLoading(false)
    }
  }

  const triggerSync = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/sync`, { method: 'POST' })
      const data = await response.json()
      showToast(data.message, "success")
    } catch (error) {
      console.error('Error triggering sync:', error)
      showToast("Failed to trigger synchronization", "error")
    }
  }

  const updateConfig = async (newConfig: Partial<Record<string, any>>) => {
    try {
      const updatedConfig = { ...config, ...newConfig }
      const response = await fetch(`${API_BASE_URL}/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedConfig),
      })
      const data = await response.json()
      setConfig(data.new_config)
      showToast("The new configuration has been saved", "success")
    } catch (error) {
      console.error('Error updating config:', error)
      showToast("Failed to update configuration", "error")
    }
  }

  const updateGroupMappings = (newMappings: { checkGroup: string; referenceGroup: string }[]) => {
    setGroupMappings(newMappings)
    const newGroupMapping = newMappings.reduce((acc, mapping) => {
      acc[mapping.checkGroup] = mapping.referenceGroup
      return acc
    }, {} as Record<string, string>)
    updateConfig({ GROUP_MAPPING: newGroupMapping })
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            CardDAV Sync Admin Panel
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            Manage your CardDAV synchronization settings and operations
          </p>
        </div>
        
        <div className="mt-10 space-y-8">
          <StatusCard status={status} onRefresh={fetchStatus} onTriggerSync={triggerSync} />

          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-2xl">Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <GroupMappings groupMappings={groupMappings} onUpdate={updateGroupMappings} />

              <Separator />

              <ConfigSettings config={config!} onUpdate={(key, value) => updateConfig({ [key]: value })} />
            </CardContent>
            <CardFooter className="bg-gray-50">
              <Button onClick={() => updateConfig(config || {})} className="w-full">
                <Settings className="mr-2 h-4 w-4" />
                Save Configuration
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}