# RBAC Guide — Hackathon Participants

## Your Access

You have the **Azure AI User** role on the Foundry resource. Here's what that means:

| You CAN | You CANNOT |
|---------|------------|
| Use models already deployed (GPT-4.1, etc.) | Deploy or delete models |
| Create and run agents | Create new Foundry resources |
| Use Playgrounds | Change network/security settings |
| Run evaluations | Assign roles to others |
| Upload files and datasets | Create model deployments |
| Use the Foundry SDK and API | Modify connections |
| Create and manage tracing | |

## Why?

Foundry separates **management actions** (deploying models, configuring security) from **development actions** (building agents, running evals). Azure AI User gives you full development access without management permissions.

The models you need are already deployed. You use them — you don't need to deploy them yourself.

## Document Intelligence

You also have the **Cognitive Services User** role on the Document Intelligence resource. This grants data plane access to call the `analyze_document` API — which the workflow uses to extract text and tables from PDF attachments.

| Role | Resource | Purpose |
|------|----------|---------|
| Azure AI User | Foundry resource | Use GPT-4.1 via Agent Framework SDK |
| Cognitive Services User | Document Intelligence resource | Extract text/tables from PDFs |
| Reader | Resource Group | See resources in the Azure portal |
