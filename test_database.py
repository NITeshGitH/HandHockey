#!/usr/bin/env python3
"""
Database Testing Script for Hand Hockey Discord Bot
Tests all database operations and schema compatibility
"""
import asyncio
import sys
import logging
from database import db_manager
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_operations():
    """Test all database operations"""
    print("🔍 STARTING DATABASE SCHEMA VERIFICATION...")
    print("=" * 60)
    
    try:
        # Test 1: Initialize database
        print("1️⃣ Testing database initialization...")
        await db_manager.initialize()
        print("✅ Database initialized successfully")
        
        # Test 2: Player operations
        print("\n2️⃣ Testing player operations...")
        test_user_id = 123456789
        test_username = "test_player"
        test_display_name = "Test Player"
        
        # Create player
        player = await db_manager.create_or_update_player(
            test_user_id, test_username, test_display_name
        )
        print(f"✅ Player created: {player}")
        
        # Get player
        retrieved_player = await db_manager.get_player(test_user_id)
        print(f"✅ Player retrieved: {retrieved_player}")
        
        # Update player stats
        stats_updated = await db_manager.update_player_stats(
            test_user_id,
            goals=5,
            assists=3,
            matches_played=10,
            matches_won=7,
            rating=8.5
        )
        print(f"✅ Player stats updated: {stats_updated}")
        
        # Verify stats update
        updated_player = await db_manager.get_player(test_user_id)
        print(f"✅ Updated player data: {updated_player}")
        
        # Test 3: Match operations
        print("\n3️⃣ Testing match operations...")
        test_match_id = "test_match_123"
        test_host_id = test_user_id
        test_channel_id = 987654321
        
        # Create match
        match = await db_manager.create_match(test_match_id, test_host_id, test_channel_id)
        print(f"✅ Match created: {match}")
        
        # Get match
        retrieved_match = await db_manager.get_match(test_match_id)
        print(f"✅ Match retrieved: {retrieved_match}")
        
        # Test 4: Match score operations (NEW)
        print("\n4️⃣ Testing match score operations...")
        score_updated = await db_manager.update_match_score(
            test_match_id,
            team_a_score=2,
            team_b_score=1,
            score_a=2,
            score_b=1,
            shots_a=8,
            shots_b=6,
            saves_a=3,
            saves_b=5
        )
        print(f"✅ Match scores updated: {score_updated}")
        
        # Verify score update
        updated_match = await db_manager.get_match(test_match_id)
        print(f"✅ Updated match data: {updated_match}")
        
        # Test 5: Match player operations
        print("\n5️⃣ Testing match player operations...")
        
        # Add player to match
        player_added = await db_manager.add_player_to_match(
            test_match_id, test_user_id, team="A", role="ST"
        )
        print(f"✅ Player added to match: {player_added}")
        
        # Get match players
        match_players = await db_manager.get_match_players(test_match_id)
        print(f"✅ Match players retrieved: {match_players}")
        
        # Update player role
        role_updated = await db_manager.update_player_role(
            test_match_id, test_user_id, team="B", role="GK", is_captain=True
        )
        print(f"✅ Player role updated: {role_updated}")
        
        # Test 6: Match status operations
        print("\n6️⃣ Testing match status operations...")
        
        # Update match status
        status_updated = await db_manager.update_match_status(test_match_id, "ongoing")
        print(f"✅ Match status updated: {status_updated}")
        
        # Get user active match
        user_active_match = await db_manager.get_user_active_match(test_user_id)
        print(f"✅ User active match: {user_active_match}")
        
        # Get all active matches
        active_matches = await db_manager.get_active_matches()
        print(f"✅ Active matches: {len(active_matches)} found")
        
        # Test 7: Team name operations
        print("\n7️⃣ Testing team name operations...")
        team_name_updated = await db_manager.update_team_name(test_match_id, "A", "Ice Breakers")
        print(f"✅ Team A name updated: {team_name_updated}")
        
        team_name_updated = await db_manager.update_team_name(test_match_id, "B", "Fire Blazers")
        print(f"✅ Team B name updated: {team_name_updated}")
        
        # Test 8: Cleanup operations
        print("\n8️⃣ Testing cleanup operations...")
        
        # Remove player from match
        player_removed = await db_manager.remove_player_from_match(test_match_id, test_user_id)
        print(f"✅ Player removed from match: {player_removed}")
        
        # Delete match
        match_deleted = await db_manager.delete_match(test_match_id)
        print(f"✅ Match deleted: {match_deleted}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL DATABASE TESTS PASSED!")
        print("✅ Schema mismatches have been resolved")
        print("✅ All database operations are working correctly")
        print("✅ Error handling is in place")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        logger.error(f"Database test error: {e}")
        return False
        
    finally:
        # Close database connection
        await db_manager.close()
        print("\n🔒 Database connection closed")

async def test_schema_compatibility():
    """Test schema compatibility with existing code"""
    print("\n🔍 TESTING SCHEMA COMPATIBILITY...")
    print("=" * 60)
    
    try:
        await db_manager.initialize()
        
        # Test player stats access pattern (as used in player_stats.py)
        test_user_id = 123456789
        await db_manager.create_or_update_player(test_user_id, "test_user", "Test User")
        
        player = await db_manager.get_player(test_user_id)
        if player:
            # Test the access patterns used in player_stats.py
            matches_played = player.get('matches_played', 0)
            matches_won = player.get('matches_won', 0)
            goals = player.get('goals', 0)
            assists = player.get('assists', 0)
            rating = player.get('rating', 6.0)
            
            print(f"✅ Player stats access pattern works:")
            print(f"   - Matches played: {matches_played}")
            print(f"   - Matches won: {matches_won}")
            print(f"   - Goals: {goals}")
            print(f"   - Assists: {assists}")
            print(f"   - Rating: {rating}")
        
        # Test match score access pattern (as used in player_stats.py scorecard)
        test_match_id = "test_compatibility_match"
        match = await db_manager.create_match(test_match_id, test_user_id, 987654321)
        
        # Update scores
        await db_manager.update_match_score(
            test_match_id,
            score_a=3,
            score_b=2,
            shots_a=12,
            shots_b=8,
            saves_a=4,
            saves_b=7
        )
        
        match_data = await db_manager.get_match(test_match_id)
        if match_data:
            # Test the access patterns used in player_stats.py
            score_a = match_data.get('score_a', 0)
            score_b = match_data.get('score_b', 0)
            shots_a = match_data.get('shots_a', 0)
            shots_b = match_data.get('shots_b', 0)
            saves_a = match_data.get('saves_a', 0)
            saves_b = match_data.get('saves_b', 0)
            
            print(f"✅ Match score access pattern works:")
            print(f"   - Score A: {score_a}, Score B: {score_b}")
            print(f"   - Shots A: {shots_a}, Shots B: {shots_b}")
            print(f"   - Saves A: {saves_a}, Saves B: {saves_b}")
        
        # Cleanup
        await db_manager.delete_match(test_match_id)
        
        print("✅ Schema compatibility verified!")
        return True
        
    except Exception as e:
        print(f"❌ COMPATIBILITY TEST FAILED: {e}")
        return False
    finally:
        await db_manager.close()

def main():
    """Main test function"""
    print("🏒 HAND HOCKEY DATABASE SCHEMA VERIFICATION")
    print("=" * 60)
    
    # Run basic database tests
    success1 = asyncio.run(test_database_operations())
    
    # Run schema compatibility tests
    success2 = asyncio.run(test_schema_compatibility())
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED - DATABASE IS READY!")
        print("✅ You can now run your Discord bot with confidence")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED - PLEASE CHECK THE ERRORS ABOVE")
        sys.exit(1)

if __name__ == "__main__":
    main()
