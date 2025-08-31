import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DocumentationHeader from '@/components/documentation/DocumentationHeader';
import OverviewTab from '@/components/documentation/OverviewTab';
import ApiReferenceTab from '@/components/documentation/ApiReferenceTab';
import ScoringAlgorithmTab from '@/components/documentation/ScoringAlgorithmTab';
import ExamplesTab from '@/components/documentation/ExamplesTab';

const Documentation = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <DocumentationHeader />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="overview" className="space-y-8" data-tabs-container>
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 h-auto gap-1 p-1">
            <TabsTrigger 
              value="overview" 
              data-value="overview"
              className="text-xs sm:text-sm py-2 px-2 sm:px-3"
            >
              Overview
            </TabsTrigger>
            <TabsTrigger 
              value="api-reference" 
              data-value="api-reference"
              className="text-xs sm:text-sm py-2 px-2 sm:px-3"
            >
              API Reference
            </TabsTrigger>
            <TabsTrigger 
              value="scoring" 
              data-value="scoring"
              className="text-xs sm:text-sm py-2 px-2 sm:px-3"
            >
              Scoring Algorithm
            </TabsTrigger>
            <TabsTrigger 
              value="examples" 
              data-value="examples"
              className="text-xs sm:text-sm py-2 px-2 sm:px-3"
            >
              Examples
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" data-value="overview" className="space-y-6">
            <OverviewTab />
          </TabsContent>

          <TabsContent value="api-reference" data-value="api-reference" className="space-y-6">
            <ApiReferenceTab />
          </TabsContent>

          <TabsContent value="scoring" data-value="scoring" className="space-y-6">
            <ScoringAlgorithmTab />
          </TabsContent>

          <TabsContent value="examples" data-value="examples" className="space-y-6">
            <ExamplesTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Documentation;
