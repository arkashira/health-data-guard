```markdown
# Dataflow Architecture

## External Data Sources
- **Healthcare Providers**: EHR systems, patient portals
- **Educational Institutions**: Student information systems, learning management systems
- **Regulatory Bodies**: State health and education departments, HIPAA compliance databases
- **Third-Party Data Vendors**: Healthcare analytics providers, educational data providers

## Ingestion Layer
```
[External Sources] --> [API Gateway] --> [Data Ingestion Service] --> [Auth Service]
```
- **API Gateway**: Manages and routes incoming data requests
- **Data Ingestion Service**: Handles data validation, normalization, and initial processing
- **Auth Service**: Ensures data sources are authenticated and authorized

## Processing/Transform Layer
```
[Data Ingestion Service] --> [Data Processing Service] --> [Compliance Engine] --> [Auth Service]
```
- **Data Processing Service**: Performs data transformation, enrichment, and aggregation
- **Compliance Engine**: Ensures data compliance with state-level regulations and standards (e.g., HIPAA, FERPA)

## Storage Tier
```
[Data Processing Service] --> [Secure Data Lake] --> [Auth Service]
[Compliance Engine] --> [Compliance Audit Logs] --> [Auth Service]
```
- **Secure Data Lake**: Stores raw and processed data in a secure, encrypted format
- **Compliance Audit Logs**: Maintains logs of all data access and processing activities for audit purposes

## Query/Serving Layer
```
[Auth Service] --> [Query Service] --> [Secure Data Lake]
[Auth Service] --> [Compliance Engine] --> [Compliance Audit Logs]
```
- **Query Service**: Handles data queries from authorized users and applications
- **Compliance Engine**: Ensures query results comply with relevant regulations

## Egress to User
```
[Query Service] --> [API Gateway] --> [User Applications]
```
- **API Gateway**: Routes query results back to user applications
- **User Applications**: Includes dashboards, reporting tools, and other interfaces for end-users

## Auth Boundaries
- **External Sources**: Authenticated via API Gateway and Auth Service
- **Data Ingestion Service**: Authenticated via Auth Service
- **Data Processing Service**: Authenticated via Auth Service
- **Compliance Engine**: Authenticated via Auth Service
- **Secure Data Lake**: Access controlled via Auth Service
- **Compliance Audit Logs**: Access controlled via Auth Service
- **Query Service**: Authenticated via Auth Service
- **User Applications**: Authenticated via API Gateway and Auth Service
```