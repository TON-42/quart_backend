## Steps

### 1. Modify the Model:

- Update the user model to include a new field `registration_date` with the appropriate data type (e.g., `DateTime`).

### 2. Create a Migration:

- Use Alembic to generate a new migration script that adds the `registration_date` field to the user table.

### 3. Apply the Migration:

- Run the migration to update the production database schema.

### 4. Push the Code Changes:

- Commit and push the changes to your repository.

### 5. Apply the Migration on Production:

- Use the DigitalOcean console to apply the migration to the production database.

## Detailed Instructions

### Step 1: Modify the Model

Edit the `User` class in `models.py` to include the `registration_date` field:
```
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    Table,
    Text,
    DateTime,  # Add DateTime import
    create_engine,
)
# ... other imports ...
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    has_profile = Column(Boolean, default=False)
    words = Column(BigInteger, default=0)
    registration_date = Column(DateTime, nullable=True)  # Add this line
    chats = relationship("Chat", secondary=users_chats, back_populates="users")
    agreed_chats = relationship(
        "Chat", secondary=agreed_users_chats, back_populates="agreed_chats"
    )
# ... rest of the file ...
```
### Step 2: Create a Migration Script

#### 1. Ensure Alembic is installed and configured:
- Make sure you have Alembic installed globally. If not, install it using pip install alembic.

### 2. Generate a new migration:
- Open a terminal and navigate to your project's root directory where the alembic.ini file is located.
- Run the following command to generate a new migration script:
`alembic revision --autogenerate -m "Add registration_date to users table"`

- /This command will create a new migration file in the alembic/versions directory. Alembic will detect the change in the model and include it in the migration script.

### 3. Review the migration script:
- Open the newly created migration script in the alembic/versions directory.
- Ensure the script contains the necessary changes to add the registration_date column. It should look something like this:
```
from alembic import op
import sqlalchemy as sa
# revision identifiers, used by Alembic.
revision = 'your_revision_id'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None
def upgrade():
    op.add_column('users', sa.Column('registration_date', sa.DateTime(), nullable=True))
def downgrade():
    op.drop_column('users', 'registration_date')
```
### 3: Apply the Migration Locally
- If you want to test the migration locally before applying it to production, you can run:
`alembic upgrade head`

### 4: Push the Code Changes

## 5: Apply the Migration on the Production Database
- Wait for Automatic Deployment:
- After pushing your changes, wait for your automatic deployment process to complete. This process should handle pulling the latest changes and updating the application on your DigitalOcean Droplet.
- Access the DigitalOcean Console:
```
Log into your DigitalOcean account and navigate to the Droplet or application running your backend.

Use the console provided by DigitalOcean to access the command line interface of your Droplet.

Navigate to the Alembic Directory:

Change to the directory where the alembic.ini file is located:

cd /path/to/your/project

Apply the Migration:

Run the Alembic upgrade command to apply the migration:

alembic upgrade head
```