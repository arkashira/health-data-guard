```markdown
# Technical Specification: health-data-guard

## Stack
- **Language**: Python (3.11+)
- **Framework**: FastAPI (for API), Django (for admin panel)
- **Runtime**: Docker containers orchestrated by AWS ECS
- **Database**: PostgreSQL (with AWS RDS)
- **Search**: Elasticsearch (for compliance rule matching)
- **Auth**: AWS Cognito
- **Storage**: AWS S3 (for encrypted data backups)

## Hosting
- **Free-tier-first**: AWS Free Tier (12 months)
  - **EC2**: t2.micro instances
  - **RDS**: PostgreSQL (750 hours/month)
  - **S3**: 5GB standard storage
  - **Lambda**: 1M free requests/month
- **Production**: AWS (paid tiers)
  - **ECS**: Fargate for serverless containers
  - **RDS**: Multi-AZ deployment for high availability
  - **CloudFront**: CDN for static assets and API caching

## Data Model
### Tables/Collections
1. **Users**
   - `user_id` (UUID, primary key)
   - `email` (string, unique)
   - `hashed_password` (string)
   - `role` (string, enum: admin, user, auditor)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. **Organizations**
   - `org_id` (UUID, primary key)
   - `name` (string)
   - `industry` (string, enum: healthcare, education, other)
   - `compliance_requirements` (JSONB, array of strings)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

3. **DataSources**
   - `data_source_id` (UUID, primary key)
   - `org_id` (UUID, foreign key to Organizations)
   - `name` (string)
   - `description` (string)
   - `data_type` (string, enum: PII, PHI, educational_records)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

4. **ComplianceRules**
   - `rule_id` (UUID, primary key)
   - `state` (string)
   - `regulation` (string)
   - `description` (string)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

5. **AuditLogs**
   - `log_id` (UUID, primary key)
   - `user_id` (UUID, foreign key to Users)
   - `action` (string)
   - `entity_type` (string)
   - `entity_id` (UUID)
   - `details` (JSONB)
   - `created_at` (timestamp)

## API Surface
1. **POST /api/auth/register**
   - Purpose: Register a new user.
2. **POST /api/auth/login**
   - Purpose: Authenticate a user and return a JWT token.
3. **GET /api/organizations**
   - Purpose: List all organizations the user has access to.
4. **POST /api/organizations**
   - Purpose: Create a new organization.
5. **GET /api/datasources**
   - Purpose: List all data sources for an organization.
6. **POST /api/datasources**
   - Purpose: Create a new data source.
7. **GET /api/compliancerules**
   - Purpose: List all compliance rules.
8. **POST /api/auditlogs**
   - Purpose: Log an audit event.
9. **GET /api/auditlogs**
   - Purpose: Retrieve audit logs for an organization.
10. **GET /api/compliance/status**
    - Purpose: Check compliance status for an organization.

## Security Model
- **Authentication**: JWT tokens issued by AWS Cognito.
- **Authorization**: Role-based access control (RBAC) implemented via middleware.
- **Secrets Management**: AWS Secrets Manager for storing database credentials and API keys.
- **IAM**: Fine-grained IAM policies for AWS services.
- **Data Encryption**: AES-256 encryption for data at rest (AWS KMS) and in transit (TLS 1.2+).

## Observability
- **Logs**: AWS CloudWatch Logs for application and infrastructure logs.
- **Metrics**: AWS CloudWatch Metrics for monitoring API performance, error rates, and compliance checks.
- **Traces**: AWS X-Ray for distributed tracing of API requests.

## Build/CI
- **CI/CD Pipeline**: GitHub Actions for continuous integration and deployment.
  - **Build**: Docker images built and pushed to AWS ECR.
  - **Test**: Unit and integration tests run on every push to the main branch.
  - **Deploy**: Automated deployment to AWS ECS using AWS CodeDeploy.
- **Infrastructure as Code**: AWS CloudFormation for managing infrastructure.
```