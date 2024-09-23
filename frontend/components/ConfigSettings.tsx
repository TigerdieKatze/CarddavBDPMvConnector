import React from 'react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type ConfigSettingsProps = {
  config: Record<string, any>;
  onUpdate: (key: string, value: any) => void;
};

export const ConfigSettings: React.FC<ConfigSettingsProps> = ({ config, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Group Settings</h3>
        <div className="space-y-2">
          <Label htmlFor="default-group">Default Group</Label>
          <Input
            id="default-group"
            value={config?.DEFAULT_GROUP}
            onChange={(e) => onUpdate('DEFAULT_GROUP', e.target.value)}
          />
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="apply-group-mapping"
            checked={config?.APPLY_GROUP_MAPPING_TO_PARENTS}
            onCheckedChange={(checked) => onUpdate('APPLY_GROUP_MAPPING_TO_PARENTS', checked)}
          />
          <Label htmlFor="apply-group-mapping">Apply Group Mapping to Parents</Label>
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="apply-default-group"
            checked={config?.APPLY_DEFAULT_GROUP_TO_PARENTS}
            onCheckedChange={(checked) => onUpdate('APPLY_DEFAULT_GROUP_TO_PARENTS', checked)}
          />
          <Label htmlFor="apply-default-group">Apply Default Group to Parents</Label>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Sync Settings</h3>
        <div className="space-y-2">
          <Label htmlFor="run-schedule">Run Schedule</Label>
          <Select
            value={config?.RUN_SCHEDULE}
            onValueChange={(value) => onUpdate('RUN_SCHEDULE', value)}
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
            onChange={(e) => onUpdate('NOTIFICATION_EMAIL', e.target.value)}
          />
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            id="dry-run"
            checked={config?.DRY_RUN}
            onCheckedChange={(checked) => onUpdate('DRY_RUN', checked)}
          />
          <Label htmlFor="dry-run">Dry Run</Label>
        </div>
      </div>
    </div>
  );
};
