import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2, RefreshCw, Loader2, Server } from "lucide-react";

type StatusCardProps = {
  status: { details: string; last_run: string; status: string } | null;
  onRefresh: () => void;
  onTriggerSync: () => void;
};

export const StatusCard: React.FC<StatusCardProps> = ({ status, onRefresh, onTriggerSync }) => {
  return (
    <Card className="shadow-lg">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-2xl">Sync Status</CardTitle>
          <Badge variant={
              status?.status === "Completed" ? "default" :
                status?.status === "In progress" ? "default" :
                  "destructive"
            }
          >
            {status?.status === "Completed" ? (
              <><CheckCircle2 className="mr-1 h-4 w-4" /> Sync Successful</>
            ) : status?.status === "In progress" ? (
              <><Loader2 className="mr-1 h-4 w-4 animate-spin" /> Sync In Progress</>
            ) : (
              <><AlertCircle className="mr-1 h-4 w-4" /> Sync Issue</>
            )}
          </Badge>
        </div>
        <CardDescription>{status?.details || "Status unknown"}</CardDescription>
      </CardHeader>
      <CardFooter className="bg-gray-50">
        <div className="flex justify-between w-full">
          <Button variant="outline" onClick={onRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Status
          </Button>
          <Button onClick={onTriggerSync}>
            <Server className="mr-2 h-4 w-4" />
            Trigger Sync
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};