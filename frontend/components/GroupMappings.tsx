import React from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Trash2 } from "lucide-react";
import { motion, AnimatePresence } from 'framer-motion';

type GroupMapping = {
  checkGroup: string;
  referenceGroup: string;
};

type GroupMappingsProps = {
  groupMappings: GroupMapping[];
  onUpdate: (newMappings: GroupMapping[]) => void;
};

export const GroupMappings: React.FC<GroupMappingsProps> = ({ groupMappings, onUpdate }) => {
  const addGroupMapping = () => {
    onUpdate([...groupMappings, { checkGroup: '', referenceGroup: '' }]);
  };

  const updateMapping = (index: number, updatedMapping: GroupMapping) => {
    const newMappings = [...groupMappings];
    newMappings[index] = updatedMapping;
    onUpdate(newMappings);
  };

  const removeMapping = (index: number) => {
    const newMappings = groupMappings.filter((_, i) => i !== index);
    onUpdate(newMappings);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Group Mappings</h3>
      <AnimatePresence>
        {groupMappings.map((mapping, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="flex items-center space-x-2 mb-2"
          >
            <Input
              placeholder="Check Group"
              value={mapping.checkGroup}
              onChange={(e) => updateMapping(index, { ...mapping, checkGroup: e.target.value })}
              className="flex-1"
            />
            <Input
              placeholder="Reference Group"
              value={mapping.referenceGroup}
              onChange={(e) => updateMapping(index, { ...mapping, referenceGroup: e.target.value })}
              className="flex-1"
            />
            <Button variant="destructive" size="icon" onClick={() => removeMapping(index)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </motion.div>
        ))}
      </AnimatePresence>
      <Button onClick={addGroupMapping} className="w-full bg-primary hover:bg-primary-dark transition-colors duration-200">
        <Plus className="mr-2 h-4 w-4" />
        Add Group Mapping
      </Button>
    </div>
  );
};