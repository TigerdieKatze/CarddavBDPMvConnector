import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2, RefreshCw, Loader2, Server } from "lucide-react";
import { motion } from 'framer-motion';

type StatusCardProps = {
  status: { details: string; last_run: string; status: string } | null;
  onRefresh: () => void;
  onTriggerSync: () => void;
  autoRefresh: boolean;
};

export const StatusCard: React.FC<StatusCardProps> = ({ status, onRefresh, onTriggerSync, autoRefresh }) => {
  React.useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (autoRefresh) {
      intervalId = setInterval(() => {
        onRefresh();
      }, 5000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, onRefresh]);
  
  return (
    <Card className="shadow-lg overflow-hidden">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-2xl">Sync Status</CardTitle>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Badge variant={
                status?.status === "Completed" ? "default" :
                  status?.status === "In progress" ? "default" :
                    "destructive"
              }
              className="text-sm font-medium px-2 py-1"
            >
              {status?.status === "Completed" ? (
                <><CheckCircle2 className="mr-1 h-4 w-4" /> Sync Successful</>
              ) : status?.status === "In progress" ? (
                <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Sync In Progress</>
              ) : (
                <><AlertCircle className="mr-1 h-4 w-4" /> Sync Issue</>
              )}
            </Badge>
          </motion.div>
        </div>
        <CardDescription>{status?.details || "Status unknown"}</CardDescription>
      </CardHeader>
      <CardFooter className="bg-gray-50">
        <div className="flex justify-between w-full">
          <Button variant="outline" onClick={onRefresh} className="hover:bg-gray-200 transition-colors duration-200">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Status
          </Button>
          <Button onClick={onTriggerSync} className="bg-primary hover:bg-primary-dark transition-colors duration-200">
            <Server className="mr-2 h-4 w-4" />
            Trigger Sync
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};