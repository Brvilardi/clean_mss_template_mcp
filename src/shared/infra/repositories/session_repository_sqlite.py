import sqlite3
import os
import logging
from typing import List, Dict

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.dto.session_sqlite_dto import SessionSQLiteDTO
from src.shared.infra.external.reinvent.reinvent_catalog_client import ReinventCatalogClient

logger = logging.getLogger(__name__)


class SessionRepositorySQLite(ISessionRepository):
    """SQLite implementation of the Session Repository."""
    
    DB_PATH = "src/shared/infra/external/sqlite/reinvent_sessions.db"
    
    def __init__(self):
        """
        Initialize the repository, create database if needed, and auto-populate if empty.
        """
        self._ensure_directory_exists()
        self._initialize_database()
        self._auto_populate_if_empty()
    
    def _ensure_directory_exists(self):
        """Create the directory for the database file if it doesn't exist."""
        db_dir = os.path.dirname(self.DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created directory: {db_dir}")
    
    def _initialize_database(self):
        """Create the sessions table and triggers if they don't exist."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    short_id TEXT,
                    title TEXT NOT NULL,
                    abstract TEXT,
                    session_type TEXT,
                    venue_name TEXT,
                    venue_room TEXT,
                    start_datetime TEXT,
                    end_datetime TEXT,
                    day TEXT,
                    speakers_json TEXT,
                    topics_json TEXT,
                    areas_of_interest_json TEXT,
                    level TEXT,
                    level_value INTEGER,
                    features_json TEXT,
                    seat_capacity INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create trigger for updated_at
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_sessions_timestamp 
                AFTER UPDATE ON sessions
                FOR EACH ROW
                BEGIN
                    UPDATE sessions SET updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = NEW.session_id;
                END
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database schema initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def _auto_populate_if_empty(self):
        """Auto-populate database from API if it's empty."""
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                logger.info("Database is empty, auto-populating from API")
                try:
                    self.sync_sessions_from_api()
                except ConnectionError as e:
                    logger.warning(f"Failed to auto-populate database: {str(e)}")
                    # Continue with empty database
                    
        except sqlite3.Error as e:
            logger.error(f"Error checking database: {str(e)}")
            raise
    
    def _fetch_from_external_api(self) -> List[dict]:
        """
        Fetch sessions from the external re:invent catalog API.
        
        Returns:
            List of session dictionaries from the API
            
        Raises:
            ConnectionError: If API is unreachable
        """
        client = ReinventCatalogClient()
        return client.fetch_sessions()
    
    def _parse_api_session_to_entity(self, api_session: dict) -> Session:
        """
        Parse API session data to Session entity.
        
        Args:
            api_session: Raw session data from API
            
        Returns:
            Session entity
            
        Raises:
            EntityError: If session data is invalid
        """
        try:
            # Extract nested fields with safe defaults
            venue_name = api_session.get('venue', {}).get('displayName', '')
            session_type = api_session.get('type', {}).get('displayName', '')
            level_display = api_session.get('level', {}).get('displayName', '')
            level_value = api_session.get('level', {}).get('value', 100)
            
            # Extract list fields
            speakers = [
                {
                    'displayName': speaker.get('displayName', ''),
                    'company': speaker.get('company', '')
                }
                for speaker in api_session.get('speakers', [])
            ]
            
            topics = [
                topic.get('displayName', '')
                for topic in api_session.get('topics', [])
            ]
            
            areas_of_interest = [
                area.get('displayName', '')
                for area in api_session.get('areaOfInterest', [])
            ]
            
            features = [
                feature.get('displayName', '')
                for feature in api_session.get('features', [])
            ]
            
            return Session(
                session_id=api_session.get('id', ''),
                short_id=api_session.get('shortId', ''),
                title=api_session.get('title', ''),
                abstract=api_session.get('abstract', ''),
                session_type=session_type,
                venue_name=venue_name,
                venue_room=api_session.get('venueRoomName', ''),
                start_datetime=api_session.get('startDateTime', ''),
                end_datetime=api_session.get('endDateTime', ''),
                day=api_session.get('day', ''),
                speakers=speakers,
                topics=topics,
                areas_of_interest=areas_of_interest,
                level=level_display,
                level_value=level_value,
                features=features,
                seat_capacity=api_session.get('seatCapacity', 0)
            )
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error parsing API session: {str(e)}")
            raise EntityError(f"Invalid session data: {str(e)}")
    
    def _upsert_session(self, session: Session, cursor: sqlite3.Cursor):
        """
        Insert or replace a session in the database.
        
        Args:
            session: Session entity to upsert
            cursor: SQLite cursor for the operation
        """
        dto = SessionSQLiteDTO.from_entity(session)
        data = dto.to_sqlite()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (
                session_id, short_id, title, abstract, session_type,
                venue_name, venue_room, start_datetime, end_datetime, day,
                speakers_json, topics_json, areas_of_interest_json,
                level, level_value, features_json, seat_capacity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['session_id'], data['short_id'], data['title'], data['abstract'],
            data['session_type'], data['venue_name'], data['venue_room'],
            data['start_datetime'], data['end_datetime'], data['day'],
            data['speakers_json'], data['topics_json'], data['areas_of_interest_json'],
            data['level'], data['level_value'], data['features_json'],
            data['seat_capacity']
        ))
    
    def get_all_sessions(self) -> List[Session]:
        """
        Returns all sessions from storage.
        
        Returns:
            List of Session entities
        """
        try:
            conn = sqlite3.connect(self.DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sessions")
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                row_dict = dict(row)
                dto = SessionSQLiteDTO.from_sqlite(row_dict)
                sessions.append(dto.to_entity())
            
            logger.info(f"Retrieved {len(sessions)} sessions from database")
            return sessions
            
        except sqlite3.Error as e:
            logger.error(f"Database error in get_all_sessions: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in get_all_sessions: {str(e)}")
            raise
    
    def get_session_by_id(self, session_id: str) -> Session:
        """
        Returns a specific session by ID.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Session entity
            
        Raises:
            NoItemsFound: If session with given ID is not found
        """
        try:
            conn = sqlite3.connect(self.DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                raise NoItemsFound("session_id")
            
            row_dict = dict(row)
            dto = SessionSQLiteDTO.from_sqlite(row_dict)
            return dto.to_entity()
            
        except NoItemsFound:
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error in get_session_by_id: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in get_session_by_id: {str(e)}")
            raise
    
    def sync_sessions_from_api(self) -> Dict[str, int]:
        """
        Fetches data from external API and updates storage.
        
        Returns:
            Dictionary with keys 'inserted' and 'updated' containing counts
            
        Raises:
            ConnectionError: If external API is unreachable
        """
        try:
            # Fetch sessions from API
            api_sessions = self._fetch_from_external_api()
            logger.info(f"Fetched {len(api_sessions)} sessions from API")
            
            # Get existing session IDs
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("SELECT session_id FROM sessions")
            existing_ids = {row[0] for row in cursor.fetchall()}
            
            inserted_count = 0
            updated_count = 0
            
            # Process sessions in a transaction
            try:
                for api_session in api_sessions:
                    try:
                        session = self._parse_api_session_to_entity(api_session)
                        
                        if session.session_id in existing_ids:
                            updated_count += 1
                        else:
                            inserted_count += 1
                        
                        self._upsert_session(session, cursor)
                        
                    except EntityError as e:
                        logger.warning(f"Skipping invalid session: {str(e)}")
                        continue
                
                conn.commit()
                logger.info(f"Sync completed: {inserted_count} inserted, {updated_count} updated")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {str(e)}")
                raise
            finally:
                conn.close()
            
            return {
                'inserted': inserted_count,
                'updated': updated_count
            }
            
        except ConnectionError:
            raise
        except Exception as e:
            logger.error(f"Error in sync_sessions_from_api: {str(e)}")
            raise
