# SEMrush Domain Metrics Collector

Nano-service for collecting and analyzing domain metrics from SEMrush API.

## Overview

This service is responsible for:
- Collecting domain-level metrics (traffic, authority, backlinks)
- Storing historical domain performance data
- Providing analysis endpoints for domain metrics

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations
5. Start the service

## Configuration

Required environment variables:
- `SEMRUSH_API_KEY`: Your SEMrush API key
- `DATABASE_URL`: Database connection string
- See `.env.example` for all options

## Development

- Install development dependencies: `pip install -r requirements-dev.txt`
- Run tests: `pytest`
- Format code: `black .`
- Type checking: `mypy .`