# Crisis Management System - 3NF Database Schema

## Third Normal Form (3NF) Compliance

This database schema follows Third Normal Form (3NF) principles to ensure data integrity and minimize redundancy:

### 3NF Requirements Met:
1. **First Normal Form (1NF)**: All attributes contain atomic values
2. **Second Normal Form (2NF)**: No partial dependencies on composite keys
3. **Third Normal Form (3NF)**: No transitive dependencies

## Database Tables

### 1. Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**3NF Analysis**: 
- Primary key: `id`
- All non-key attributes depend only on the primary key
- No transitive dependencies

### 2. Incidents Table
```sql
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    latitude FLOAT,
    longitude FLOAT,
    address TEXT,
    image_path VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    reported_by INTEGER NOT NULL REFERENCES users(id),
    assigned_team_id INTEGER REFERENCES users(id)
);
```

**3NF Analysis**:
- Primary key: `id`
- Foreign keys: `reported_by`, `assigned_team_id` reference `users(id)`
- All attributes directly depend on the primary key
- No redundant user information stored (normalized through foreign keys)

### 3. Resources Table
```sql
CREATE TABLE resources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    description TEXT,
    availability_status VARCHAR(20) NOT NULL DEFAULT 'available',
    location VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**3NF Analysis**:
- Primary key: `id`
- All attributes functionally depend only on the primary key
- No transitive dependencies

### 4. Incident_Resources Table (Junction Table)
```sql
CREATE TABLE incident_resources (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP,
    notes TEXT,
    UNIQUE(incident_id, resource_id, assigned_at)
);
```

**3NF Analysis**:
- Primary key: `id`
- Composite unique constraint prevents duplicate assignments
- Resolves many-to-many relationship between incidents and resources
- All attributes depend on the primary key

### 5. Status_Updates Table
```sql
CREATE TABLE status_updates (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    notes TEXT,
    updated_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**3NF Analysis**:
- Primary key: `id`
- Foreign keys: `incident_id`, `updated_by`
- Tracks historical status changes
- No redundant incident or user data stored

## Relationships

### One-to-Many Relationships:
1. **Users → Incidents (Reporter)**: One user can report many incidents
2. **Users → Incidents (Assigned Team)**: One team can be assigned to many incidents
3. **Users → Status Updates**: One user can create many status updates
4. **Incidents → Status Updates**: One incident can have many status updates

### Many-to-Many Relationships:
1. **Incidents ↔ Resources**: Resolved through `incident_resources` junction table

## Indexes for Performance

```sql
-- Primary key indexes (automatic)
-- Additional indexes for frequently queried columns
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_incidents_reported_by ON incidents(reported_by);
CREATE INDEX idx_incidents_assigned_team ON incidents(assigned_team_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_incident_resources_incident ON incident_resources(incident_id);
CREATE INDEX idx_incident_resources_resource ON incident_resources(resource_id);
CREATE INDEX idx_status_updates_incident ON status_updates(incident_id);
```

## Data Integrity Constraints

### Foreign Key Constraints:
- `incidents.reported_by` → `users.id`
- `incidents.assigned_team_id` → `users.id`
- `incident_resources.incident_id` → `incidents.id`
- `incident_resources.resource_id` → `resources.id`
- `status_updates.incident_id` → `incidents.id`
- `status_updates.updated_by` → `users.id`

### Check Constraints:
```sql
ALTER TABLE users ADD CONSTRAINT chk_user_role 
    CHECK (role IN ('user', 'rescue_team', 'admin'));

ALTER TABLE incidents ADD CONSTRAINT chk_incident_priority 
    CHECK (priority IN ('low', 'medium', 'high', 'critical'));

ALTER TABLE incidents ADD CONSTRAINT chk_incident_status 
    CHECK (status IN ('pending', 'in_progress', 'resolved', 'closed'));

ALTER TABLE incidents ADD CONSTRAINT chk_incident_type 
    CHECK (incident_type IN ('fire', 'medical', 'accident', 'natural_disaster', 'crime', 'utility', 'other'));

ALTER TABLE resources ADD CONSTRAINT chk_resource_type 
    CHECK (resource_type IN ('vehicle', 'equipment', 'personnel'));

ALTER TABLE resources ADD CONSTRAINT chk_resource_status 
    CHECK (availability_status IN ('available', 'in_use', 'maintenance'));
```

## 3NF Verification Checklist

✅ **1NF Compliance**:
- All tables have primary keys
- All attributes contain atomic values
- No repeating groups

✅ **2NF Compliance**:
- All tables are in 1NF
- All non-key attributes are fully functionally dependent on primary keys
- No partial dependencies (all primary keys are single attributes)

✅ **3NF Compliance**:
- All tables are in 2NF
- No transitive dependencies exist
- All non-key attributes depend only on primary keys

## Benefits of 3NF Design

1. **Data Integrity**: Eliminates update anomalies and inconsistencies
2. **Storage Efficiency**: Minimizes data redundancy
3. **Maintainability**: Changes to data structure are localized
4. **Scalability**: Database can grow efficiently without structural issues
5. **Query Performance**: Proper indexing supports fast data retrieval

## Sample Queries

### Complex Joins Demonstrating Normalized Structure:
```sql
-- Get all incidents with reporter and assigned team details
SELECT 
    i.id,
    i.title,
    i.status,
    i.priority,
    r.full_name AS reporter_name,
    t.full_name AS team_name
FROM incidents i
JOIN users r ON i.reported_by = r.id
LEFT JOIN users t ON i.assigned_team_id = t.id
WHERE i.status = 'pending';

-- Get incidents with assigned resources
SELECT 
    i.title,
    res.name AS resource_name,
    res.resource_type,
    ir.assigned_at
FROM incidents i
JOIN incident_resources ir ON i.id = ir.incident_id
JOIN resources res ON ir.resource_id = res.id
WHERE ir.released_at IS NULL;
```

This schema ensures data consistency, eliminates redundancy, and maintains referential integrity while supporting all Crisis Management System operations efficiently.