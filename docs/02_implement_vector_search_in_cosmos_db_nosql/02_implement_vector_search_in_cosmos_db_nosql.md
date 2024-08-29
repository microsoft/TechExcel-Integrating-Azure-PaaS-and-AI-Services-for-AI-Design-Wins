---
title: 'Exercise 02: Implement contextual grounding using vector search in Azure Cosmos DB NoSQL'
layout: default
nav_order: 3
has_children: true
---

# Exercise 02 - Implement contextual grounding using vector search in Azure Cosmos DB NoSQL

## Lab Scenario

One of the most natural ways to integrate Azure OpenAI in an existing solution is to incorporate chat into an existing system. For this solution to bring the most value to an organization, however, the chat service must have access to information that may be proprietary or otherwise confidential. In this exercise, we will add custom data to augment an existing Azure OpenAI chat deployment, allowing customer service agents to review customer data in a natural language format.

## Objectives

After you complete this lab, you will be able to:

- Enable the Vector Search feature in Azure Cosmos DB NoSQL
- Define container vector policies
- Create vector indexing policies
- Generate vector embeddings using Azure OpenAI
- Peform similarity search using the `VectorDistance()` function in Cosmos DB

## Lab Duration

- **Estimated Time:** 60 minutes

1. Enable vector search (15 min)
   1. Enroll in feature
   2. Create containers (UserReviews and PropertyMaintenance)
   3. Define container vector policy and vector indexing policy.
2. Upload data and create vectors using Azure Open AI (30 min)
   1. Upload data from blob storage (User reviews and property maintenance JSON files)
   2. Vectorize text fields
   3. Write vectors to field defined in container
   4. Review data in data explorer to see what vectors look like.
   5. Update application to handle vectorizing new records?
3. Execute vector distance queries (15 min)
   1. Execute various vector searches
   2. Compare against traditional search?
   3. Add new record and then search for it? This will showcase vectorization process running against new records and making them immediately available for searching.