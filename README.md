# Wikipedia Discord Bot

## Overview

The **Wikipedia Discord Bot** is a real-time bot that connects to the Wikipedia Recent Changes stream, processes data using Kafka, and stores it in MongoDB. It offers users the ability to retrieve recent Wikipedia changes, set preferred languages, and view daily statistics. The system is containerized with Docker and deployed on Azure using Docker Compose. An NGINX proxy handles routing to the appropriate services.

## Features

- **Real-Time Data Ingestion:** Stream Wikipedia recent changes via Kafka.
- **Language Filtering:** Dynamic filtering of events by language.
- **Discord Bot Commands:** For retrieving recent changes, setting language preferences, and viewing stats.
- **Data Persistence:** MongoDB for storing recent events, language preferences, and statistics.
- **Scalability:** Kafka-based architecture allows easy scaling, with potential integration of Spark Streaming.
- **Deployment:** Docker Compose for local development; deployable on Azure Web App Service.

## Deployment (Local Setup)

### Prerequisites

- Docker & Docker Compose installed on your machine.

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/khnur/wiki-discord-bot.git
   cd wiki-discord-bot
   ```

2. **Insert Discord Bot Token:**

   In `.env` file in the project root update Discord bot token or leave it as it is with the test token:

   ```bash
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```

3. **Run the Application:**

   ```bash
   docker compose up -d
   ```

   **Ensure the following ports are free before running:**

   - **Kafka UI:** Port 80 (proxied via NGINX)
   - **Mongo Express:** Port 8081 (proxied via NGINX)

4. **Wait for Services to Initialize:** This will pull necessary images and set up Kafka, MongoDB, and the Discord bot.

### Accessing Services Locally

- **Kafka UI:** [http://localhost](http://localhost)
- **Mongo Express:** [http://localhost/mongo-express](http://localhost/mongo-express)

## Deployment on Azure

The project is deployed on Azure Web App Service using Docker Compose. The services are accessible via:

- **Kafka UI:** [Kafka UI](https://wiki-discord-bot-cpcjbvegguggc0gu.canadacentral-01.azurewebsites.net/)
- **Mongo Express:** [Mongo Express](https://wiki-discord-bot-cpcjbvegguggc0gu.canadacentral-01.azurewebsites.net/mongo-express)

## Adding the Bot to Discord

Add the bot to your Discord server using this link: [Add to Discord](https://discord.com/oauth2/authorize?client_id=1336001141304983683\&permissions=0\&integration_type=0\&scope=bot)

## Bot Commands

- `!setLang [language_code]` – Set the default language (e.g., `!setLang en`).
- `!recent [optional_language_code]` – Retrieve the most recent Wikipedia changes (e.g., `!recent es`).
- `!stats [yyyy-mm-dd]` – Display the number of changes for a specific date (e.g., `!stats 2024-06-01`).

## Design Decisions & Trade-offs

- **Kafka for Scalability:** Kafka decouples data ingestion from processing, enabling easy scaling. Messages are produced in 5-second intervals for controlled throughput.
- **MongoDB for Flexibility:** Chosen for its schema-less design, allowing flexible storage of dynamic event data.
- **NGINX as Reverse Proxy:** Simplifies routing requests to appropriate services.
- **Dockerized Architecture:** Simplifies deployment and ensures consistency across environments.

## CI/CD Integration

CI/CD is configured via GitHub Actions to automate the build and push process to Docker Hub, enabling easy deployment to Azure Web App Service.

## Scaling Considerations

- **Kubernetes Deployment:** Services can be deployed as separate pods to improve availability.
- **Spark Streaming:** Future integration can process Kafka messages for complex analytics, aggregations, or real-time data enrichment.

## Known Issues

- **Free Azure Resource Limitation:** Deployment may be temporarily unavailable due to free-tier restrictions.

## Contributing

Feel free to fork the repository, create pull requests, and contribute to the project.
