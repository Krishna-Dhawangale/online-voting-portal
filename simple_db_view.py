"""
Simple Database Viewer - Shows raw database tables
"""

from db import get_session, voters, candidates, votes

def simple_view():
    print("📊 SIMPLE DATABASE VIEW")
    print("=" * 50)
    
    with get_session() as session:
        print("\n🗳️ VOTERS TABLE:")
        voters_data = session.execute(voters.select()).all()
        for row in voters_data:
            print(f"ID: {row[0]}, Name: {row[1]}, Aadhaar: {row[2]}, Mobile: {row[3]}, Has Voted: {row[4]}")
        
        print("\n👥 CANDIDATES TABLE:")
        candidates_data = session.execute(candidates.select()).all()
        for row in candidates_data:
            print(f"ID: {row[0]}, Name: {row[1]}, Party: {row[2]}, Created: {row[3]}")
        
        print("\n🗳️ VOTES TABLE:")
        votes_data = session.execute(votes.select()).all()
        for row in votes_data:
            print(f"Vote ID: {row[0]}, Voter ID: {row[1]}, Candidate ID: {row[2]}, Voted At: {row[3]}")

if __name__ == "__main__":
    simple_view()
