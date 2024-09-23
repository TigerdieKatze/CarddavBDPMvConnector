'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Settings, RefreshCcw } from "lucide-react"
import { StatusCard } from '@/components/StatusCard'
import { GroupMappings } from '@/components/GroupMappings'
import { ConfigSettings } from '@/components/ConfigSettings'
import { Toast } from '@/components/Toast'
import { motion } from 'framer-motion'

const API_BASE_URL = 'http://127.0.0.1:5000'

type Status = 'Completed' | 'In progress' | 'Error'

interface StatusDetails {
  details: string
  last_run: string
  status: Status
}

interface GroupMapping {
  checkGroup: string
  referenceGroup: string
}

export default function Home() {
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [status, setStatus] = useState<StatusDetails | null>(null)
  const [config, setConfig] = useState<Record<string, any> | null>(null)
  const [groupMappings, setGroupMappings] = useState<GroupMapping[]>([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  const showToast = useCallback((message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`)
      if (!response.ok) throw new Error('Network response was not ok')
      const data: StatusDetails = await response.json()
      setStatus(data)
    } catch (error) {
      console.error('Error fetching status:', error)
      showToast("Failed to fetch sync status", "error")
    }
  }, [showToast])

  const fetchConfig = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/config`)
      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setConfig(data)
      setGroupMappings(Object.entries(data.GROUP_MAPPING).map(([checkGroup, referenceGroup]) => ({
        checkGroup,
        referenceGroup: referenceGroup as string
      })))
    } catch (error) {
      console.error('Error fetching config:', error)
      showToast("Failed to fetch configuration", "error")
    } finally {
      setLoading(false)
    }
  }, [showToast])

  useEffect(() => {
    fetchStatus()
    fetchConfig()
  }, [fetchStatus, fetchConfig])

  const triggerSync = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/sync`, { method: 'POST' })
      if (!response.ok) throw new Error('Network response was not ok')
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
      if (!response.ok) throw new Error('Network response was not ok')
      const data = await response.json()
      setConfig(data.new_config)
      showToast("The new configuration has been saved", "success")
    } catch (error) {
      console.error('Error updating config:', error)
      showToast("Failed to update configuration", "error")
    }
  }

  const updateGroupMappings = (newMappings: GroupMapping[]) => {
    setGroupMappings(newMappings)
    const newGroupMapping = newMappings.reduce((acc, mapping) => {
      acc[mapping.checkGroup] = mapping.referenceGroup
      return acc
    }, {} as Record<string, string>)
    updateConfig({ GROUP_MAPPING: newGroupMapping })
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-100">
        <motion.div
          className="w-16 h-16 border-t-4 border-primary rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-100 to-gray-200 py-12 px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-7xl mx-auto"
      >
        <header className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            CardDAV Sync Admin Panel
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            Manage your CardDAV synchronization settings and operations
          </p>
        </header>
        
        <div className="mt-10 space-y-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-2xl font-bold"></CardTitle>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="auto-refresh"
                    checked={autoRefresh}
                    onCheckedChange={setAutoRefresh}
                  />
                  <Label htmlFor="auto-refresh" className="text-sm font-medium text-gray-700 flex items-center">
                    <RefreshCcw className="w-4 h-4 mr-1" />
                    Auto-refresh
                  </Label>
                </div>
              </CardHeader>
              <CardContent>
                <StatusCard
                  status={status}
                  onRefresh={fetchStatus}
                  onTriggerSync={triggerSync}
                  autoRefresh={autoRefresh}
                />
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <Card className="shadow-lg hover:shadow-xl transition-shadow duration-300">
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
                  <Settings className="mr-2 h-4 w-4" aria-hidden="true" />
                  Save Configuration
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        </div>
      </motion.div>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </main>
  )
}