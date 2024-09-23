'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, CheckCircle2, RefreshCw, Settings, X, Server, Plus, Trash2 } from "lucide-react"
import { Separator } from "@/components/ui/separator"

const API_BASE_URL = 'http://127.0.0.1:5000'

type ToastProps = {
  message: string
  type: 'success' | 'error'
  onClose: () => void
}

const Toast: React.FC<ToastProps> = ({ message, type, onClose }) => {
  return (
    <div className={`fixed bottom-4 right-4 p-4 rounded-md shadow-md ${type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white flex items-center justify-between z-50`}>
      <span>{message}</span>
      <button onClick={onClose} className="ml-4 text-white hover:text-gray-200">
        <X size={18} />
      </button>
    </div>
  )
}

type GroupMapping = {
  checkGroup: string;
  referenceGroup: string;
}

const GroupMappingItem: React.FC<{
  mapping: GroupMapping;
  onUpdate: (updatedMapping: GroupMapping) => void;
  onRemove: () => void;
}> = ({ mapping, onUpdate, onRemove }) => {
  return (
    <div className="flex items-center space-x-2 mb-2">
      <Input
        placeholder="Check Group"
        value={mapping.checkGroup}
        onChange={(e) => onUpdate({ ...mapping, checkGroup: e.target.value })}
        className="flex-1"
      />
      <Input
        placeholder="Reference Group"
        value={mapping.referenceGroup}
        onChange={(e) => onUpdate({ ...mapping, referenceGroup: e.target.value })}
        className="flex-1"
      />
      <Button variant="destructive" size="icon" onClick={onRemove}>
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  )
}

export default function Home() {
  const [status, setStatus] = useState<{ details: String, last_run: string, status: string  } | null>(null)
  const [config, setConfig] = useState<Record<string, any> | null>(null)
  const [groupMappings, setGroupMappings] = useState<GroupMapping[]>([])
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

  const updateGroupMappings = (newMappings: GroupMapping[]) => {
    setGroupMappings(newMappings)
    const newGroupMapping = newMappings.reduce((acc, mapping) => {
      acc[mapping.checkGroup] = mapping.referenceGroup
      return acc
    }, {} as Record<string, string>)
    updateConfig({ GROUP_MAPPING: newGroupMapping })
  }

  const addGroupMapping = () => {
    setGroupMappings([...groupMappings, { checkGroup: '', referenceGroup: '' }])
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
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-2xl">Sync Status</CardTitle>
                <Badge variant={status?.status === "Completed" ? "default" : "destructive"}>
                  {status?.status === "Completed" ? (
                    <><CheckCircle2 className="mr-1 h-4 w-4" /> Sync Successful</>
                  ) : (
                    <><AlertCircle className="mr-1 h-4 w-4" /> Sync Issue</>
                  )}
                </Badge>
              </div>
              <CardDescription>{status?.details || "Status unknown"}</CardDescription>
            </CardHeader>
            <CardFooter className="bg-gray-50">
              <div className="flex justify-between w-full">
                <Button variant="outline" onClick={fetchStatus}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh Status
                </Button>
                <Button onClick={triggerSync}>
                  <Server className="mr-2 h-4 w-4" />
                  Trigger Sync
                </Button>
              </div>
            </CardFooter>
          </Card>

          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-2xl">Configuration</CardTitle>
              <CardDescription>Manage your CardDAV sync settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Group Mappings</h3>
                {groupMappings.map((mapping, index) => (
                  <GroupMappingItem
                    key={index}
                    mapping={mapping}
                    onUpdate={(updatedMapping) => {
                      const newMappings = [...groupMappings]
                      newMappings[index] = updatedMapping
                      updateGroupMappings(newMappings)
                    }}
                    onRemove={() => {
                      const newMappings = groupMappings.filter((_, i) => i !== index)
                      updateGroupMappings(newMappings)
                    }}
                  />
                ))}
                <Button onClick={addGroupMapping} className="w-full">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Group Mapping
                </Button>
              </div>

              <Separator />

              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Group Settings</h3>
                  <div className="space-y-2">
                    <Label htmlFor="default-group">Default Group</Label>
                    <Input
                      id="default-group"
                      value={config?.DEFAULT_GROUP}
                      onChange={(e) => updateConfig({ DEFAULT_GROUP: e.target.value })}
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="apply-group-mapping"
                      checked={config?.APPLY_GROUP_MAPPING_TO_PARENTS}
                      onCheckedChange={(checked) => updateConfig({ APPLY_GROUP_MAPPING_TO_PARENTS: checked })}
                    />
                    <Label htmlFor="apply-group-mapping">Apply Group Mapping to Parents</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="apply-default-group"
                      checked={config?.APPLY_DEFAULT_GROUP_TO_PARENTS}
                      onCheckedChange={(checked) => updateConfig({ APPLY_DEFAULT_GROUP_TO_PARENTS: checked })}
                    />
                    <Label htmlFor="apply-default-group">Apply Default Group to Parents</Label>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Sync Settings</h3>
                  <div className="space-y-2">
                    <Label htmlFor="run-schedule">Run Schedule</Label>
                    <Select
                      value={config?.RUN_SCHEDULE}
                      onValueChange={(value) => updateConfig({ RUN_SCHEDULE: value })}
                    >
                      <SelectTrigger id="run-schedule">
                        <SelectValue placeholder="Select schedule" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="notification-email">Notification Email</Label>
                    <Input
                      id="notification-email"
                      type="email"
                      value={config?.NOTIFICATION_EMAIL}
                      onChange={(e) => updateConfig({ NOTIFICATION_EMAIL: e.target.value })}
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="dry-run"
                      checked={config?.DRY_RUN}
                      onCheckedChange={(checked) => updateConfig({ DRY_RUN: checked })}
                    />
                    <Label htmlFor="dry-run">Dry Run</Label>
                  </div>
                </div>
              </div>
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