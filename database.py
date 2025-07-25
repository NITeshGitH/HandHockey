"""
Database module for Hand Hockey Discord Bot
Handles PostgreSQL connection and operations using Neon.com
"""
import asyncio
import asyncpg
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import Config
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.connection_url = Config.DATABASE_URL
    
    async def initialize(self, max_retries: int = 3):
        """Initialize database connection pool with retry logic"""
        for attempt in range(max_retries):
            try:
                self.pool = await asyncpg.create_pool(
                    self.connection_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("Database pool created successfully")
                await self.create_tables()
                return
            except Exception as e:
                logger.error(f"Failed to initialize database (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Database initialization failed.")
                    raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            # Players table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    display_name VARCHAR(100),
                    matches_played INTEGER DEFAULT 0,
                    matches_won INTEGER DEFAULT 0,
                    matches_lost INTEGER DEFAULT 0,
                    goals INTEGER DEFAULT 0,
                    assists INTEGER DEFAULT 0,
                    saves INTEGER DEFAULT 0,
                    tackles INTEGER DEFAULT 0,
                    interceptions INTEGER DEFAULT 0,
                    hat_tricks INTEGER DEFAULT 0,
                    mvps INTEGER DEFAULT 0,
                    rating DECIMAL(4,2) DEFAULT 6.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Matches table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id VARCHAR(50) PRIMARY KEY,
                    host_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    status VARCHAR(20) DEFAULT 'waiting',
                    team_a_name VARCHAR(100) DEFAULT 'Team A',
                    team_b_name VARCHAR(100) DEFAULT 'Team B',
                    team_a_score INTEGER DEFAULT 0,
                    team_b_score INTEGER DEFAULT 0,
                    score_a INTEGER DEFAULT 0,
                    score_b INTEGER DEFAULT 0,
                    shots_a INTEGER DEFAULT 0,
                    shots_b INTEGER DEFAULT 0,
                    saves_a INTEGER DEFAULT 0,
                    saves_b INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP
                )
            """)
            
            # Match players table (many-to-many relationship)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS match_players (
                    id SERIAL PRIMARY KEY,
                    match_id VARCHAR(50) REFERENCES matches(match_id) ON DELETE CASCADE,
                    user_id BIGINT REFERENCES players(user_id) ON DELETE CASCADE,
                    team VARCHAR(1) CHECK (team IN ('A', 'B')),
                    role VARCHAR(3) CHECK (role IN ('ST', 'MF', 'DEF', 'GK')),
                    is_captain BOOLEAN DEFAULT FALSE,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(match_id, user_id)
                )
            """)
            
            # Match events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS match_events (
                    id SERIAL PRIMARY KEY,
                    match_id VARCHAR(50) REFERENCES matches(match_id) ON DELETE CASCADE,
                    event_type VARCHAR(20) NOT NULL,
                    player1_id BIGINT,
                    player2_id BIGINT,
                    team VARCHAR(1),
                    description TEXT,
                    minute INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_host ON matches(host_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_matches_status ON matches(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_match_players_match ON match_players(match_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_match_players_user ON match_players(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_match_events_match ON match_events(match_id)")
            
            logger.info("Database tables created/verified successfully")
    
    # Player operations
    async def create_or_update_player(self, user_id: int, username: str, display_name: str = None) -> Dict:
        """Create or update a player record"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO players (user_id, username, display_name, updated_at)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    username = EXCLUDED.username,
                    display_name = EXCLUDED.display_name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            """, user_id, username, display_name or username)
            return dict(result)
    
    async def get_player(self, user_id: int) -> Optional[Dict]:
        """Get player by user ID"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM players WHERE user_id = $1", user_id)
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching player {user_id}: {e}")
            return None
    
    async def update_player_stats(self, user_id: int, **stats) -> bool:
        """Update player statistics"""
        if not stats:
            return False
            
        set_clauses = []
        values = []
        param_count = 1
        
        for key, value in stats.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                continue  # Skip iterables that aren't strings
            set_clauses.append(f"{key} = ${param_count}")
            values.append(value)
            param_count += 1
        
        if not set_clauses:
            return False
        
        set_clauses.append(f"updated_at = ${param_count}")
        values.append(datetime.now())
        values.append(user_id)  # For WHERE clause
        
        query = f"""
            UPDATE players 
            SET {', '.join(set_clauses)}
            WHERE user_id = ${param_count + 1}
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *values)
            return result != "UPDATE 0"
    
    # Match operations
    async def create_match(self, match_id: str, host_id: int, channel_id: int) -> Dict:
        """Create a new match"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO matches (match_id, host_id, channel_id)
                VALUES ($1, $2, $3)
                RETURNING *
            """, match_id, host_id, channel_id)
            return dict(result)
    
    async def get_match(self, match_id: str) -> Optional[Dict]:
        """Get match by ID"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("SELECT * FROM matches WHERE match_id = $1", match_id)
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching match {match_id}: {e}")
            return None
    
    async def get_active_matches(self) -> List[Dict]:
        """Get all active matches"""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT * FROM matches 
                WHERE status IN ('waiting', 'ongoing')
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in results]
    
    async def get_user_active_match(self, user_id: int) -> Optional[Dict]:
        """Get user's active match (as host)"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT * FROM matches 
                WHERE host_id = $1 AND status IN ('waiting', 'ongoing')
                LIMIT 1
            """, user_id)
            return dict(result) if result else None
    
    async def delete_match(self, match_id: str) -> bool:
        """Delete a match"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM matches WHERE match_id = $1", match_id)
            return result != "DELETE 0"
    
    async def update_match_status(self, match_id: str, status: str) -> bool:
        """Update match status"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE matches 
                SET status = $1
                WHERE match_id = $2
            """, status, match_id)
            return result != "UPDATE 0"
    
    async def update_match_host(self, match_id: str, new_host_id: int) -> bool:
        """Update match host"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE matches 
                SET host_id = $1
                WHERE match_id = $2
            """, new_host_id, match_id)
            return result != "UPDATE 0"
    
    # Match player operations
    async def add_player_to_match(self, match_id: str, user_id: int, username: str, team: str = None, role: str = None) -> bool:
        """Add player to match (creates/updates player record first)"""
        async with self.pool.acquire() as conn:
            try:
                # Create or update player record
                await self.create_or_update_player(user_id, username, username)
                # Add player to match
                await conn.execute("""
                    INSERT INTO match_players (match_id, user_id, team, role)
                    VALUES ($1, $2, $3, $4)
                """, match_id, user_id, team, role)
                return True
            except asyncpg.UniqueViolationError:
                return False  # Player already in match
    
    async def get_match_players(self, match_id: str) -> List[Dict]:
        """Get all players in a match"""
        async with self.pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT mp.*, p.username, p.display_name
                FROM match_players mp
                JOIN players p ON mp.user_id = p.user_id
                WHERE mp.match_id = $1
                ORDER BY mp.team, mp.joined_at
            """, match_id)
            return [dict(row) for row in results]
    
    async def remove_player_from_match(self, match_id: str, user_id: int) -> bool:
        """Remove player from match"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM match_players 
                WHERE match_id = $1 AND user_id = $2
            """, match_id, user_id)
            return result != "DELETE 0"
    
    async def update_player_role(self, match_id: str, user_id: int, team: str = None, role: str = None, is_captain: bool = None) -> bool:
        """Update player's team/role in match"""
        updates = []
        values = []
        param_count = 1
        
        if team is not None:
            updates.append(f"team = ${param_count}")
            values.append(team)
            param_count += 1
        
        if role is not None:
            updates.append(f"role = ${param_count}")
            values.append(role)
            param_count += 1
        
        if is_captain is not None:
            updates.append(f"is_captain = ${param_count}")
            values.append(is_captain)
            param_count += 1
        
        if not updates:
            return False
        
        values.extend([match_id, user_id])
        
        query = f"""
            UPDATE match_players 
            SET {', '.join(updates)}
            WHERE match_id = ${param_count} AND user_id = ${param_count + 1}
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *values)
            return result != "UPDATE 0"
    
    async def update_team_name(self, match_id: str, team: str, name: str) -> bool:
        """Update team name in match"""
        column = f"team_{team.lower()}_name"
        query = f"UPDATE matches SET {column} = $1 WHERE match_id = $2"
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, name, match_id)
            return result != "UPDATE 0"
    
    async def update_match_score(self, match_id: str, **score_data) -> bool:
        """Update match score and stats"""
        if not score_data:
            return False
            
        set_clauses = []
        values = []
        param_count = 1
        
        # Allowed score fields
        allowed_fields = ['team_a_score', 'team_b_score', 'score_a', 'score_b', 
                         'shots_a', 'shots_b', 'saves_a', 'saves_b']
        
        for key, value in score_data.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not set_clauses:
            return False
        
        values.append(match_id)  # For WHERE clause
        
        query = f"""
            UPDATE matches 
            SET {', '.join(set_clauses)}
            WHERE match_id = ${param_count}
        """
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *values)
            return result != "UPDATE 0"

# Global database manager instance
db_manager = DatabaseManager()

async def init_database():
    """Initialize database connection"""
    await db_manager.initialize()

async def close_database():
    """Close database connection"""
    await db_manager.close()
