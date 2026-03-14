"""
Database Viewer for Online Voting Portal
Shows all tables and voting data in the database
"""

from db import get_session, voters, candidates, votes
from sqlalchemy import text

def view_database():
    print("=" * 80)
    print("ONLINE VOTING PORTAL - DATABASE VIEWER")
    print("=" * 80)
    
    with get_session() as session:
        print("\n📊 DATABASE TABLES AND DATA")
        print("-" * 50)
        
        # 1. View Voters Table
        print("\n🗳️  VOTERS TABLE:")
        print("-" * 30)
        voters_data = session.execute(voters.select()).all()
        if voters_data:
            print(f"{'Voter ID':<10} {'Name':<20} {'Aadhaar':<15} {'Has Voted':<10} {'Mobile':<12}")
            print("-" * 80)
            for voter in voters_data:
                print(f"{voter[0]:<10} {voter[1]:<20} {voter[2]:<15} {voter[4]:<10} {voter[3]:<12}")
        else:
            print("No voters found in database.")
        
        # 2. View Candidates Table
        print("\n👥 CANDIDATES TABLE:")
        print("-" * 30)
        candidates_data = session.execute(candidates.select()).all()
        if candidates_data:
            print(f"{'Candidate ID':<15} {'Name':<25} {'Party':<20} {'Created At':<20}")
            print("-" * 80)
            for candidate in candidates_data:
                created_at = str(candidate[3])[:19] if candidate[3] else "N/A"
                print(f"{candidate[0]:<15} {candidate[1]:<25} {candidate[2]:<20} {created_at:<20}")
        else:
            print("No candidates found in database.")
        
        # 3. View Votes Table
        print("\n🗳️  VOTES TABLE:")
        print("-" * 30)
        votes_data = session.execute(votes.select()).all()
        if votes_data:
            print(f"{'Vote ID':<10} {'Voter ID':<10} {'Candidate ID':<15} {'Voted At':<20}")
            print("-" * 65)
            for vote in votes_data:
                voted_at = str(vote[3])[:19] if vote[3] else "N/A"
                print(f"{vote[0]:<10} {vote[1]:<10} {vote[2]:<15} {voted_at:<20}")
        else:
            print("No votes found in database.")
        
        # 4. Detailed Voting Results (Who voted for whom)
        print("\n📋 DETAILED VOTING RESULTS:")
        print("-" * 40)
        
        # Join all tables to show complete voting information
        query = text("""
            SELECT 
                v.voter_id,
                v.name as voter_name,
                v.aadhaar,
                v.has_voted,
                c.name as candidate_name,
                c.party as candidate_party,
                vt.voted_at
            FROM voters v
            LEFT JOIN votes vt ON v.voter_id = vt.voter_id
            LEFT JOIN candidates c ON vt.candidate_id = c.candidate_id
            ORDER BY v.voter_id
        """)
        
        detailed_results = session.execute(query).all()
        
        if detailed_results:
            print(f"{'Voter ID':<10} {'Voter Name':<20} {'Aadhaar':<15} {'Status':<8} {'Candidate':<20} {'Party':<15} {'Voted At':<20}")
            print("-" * 110)
            
            for row in detailed_results:
                voter_id = row[0]
                voter_name = row[1]
                aadhaar = row[2]
                has_voted = row[3]
                candidate_name = row[4] if row[4] else "Not voted"
                candidate_party = row[5] if row[5] else "-"
                voted_at = str(row[6])[:19] if row[6] else "-"
                
                status = "✅ Voted" if has_voted else "⏳ Pending"
                
                print(f"{voter_id:<10} {voter_name:<20} {aadhaar:<15} {status:<8} {candidate_name:<20} {candidate_party:<15} {voted_at:<20}")
        else:
            print("No voting data found.")
        
        # 5. Vote Summary by Candidate
        print("\n📊 VOTE SUMMARY BY CANDIDATE:")
        print("-" * 40)
        
        summary_query = text("""
            SELECT 
                c.candidate_id,
                c.name as candidate_name,
                c.party,
                COUNT(vt.vote_id) as vote_count
            FROM candidates c
            LEFT JOIN votes vt ON c.candidate_id = vt.candidate_id
            GROUP BY c.candidate_id, c.name, c.party
            ORDER BY vote_count DESC
        """)
        
        summary_results = session.execute(summary_query).all()
        
        if summary_results:
            print(f"{'Rank':<6} {'Candidate':<25} {'Party':<20} {'Votes':<8} {'Percentage':<12}")
            print("-" * 80)
            
            total_votes = sum(row[3] for row in summary_results)
            
            for rank, row in enumerate(summary_results, 1):
                candidate_id = row[0]
                candidate_name = row[1]
                party = row[2]
                vote_count = row[3]
                percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
                
                print(f"{rank:<6} {candidate_name:<25} {party:<20} {vote_count:<8} {percentage:.1f}%{'':<8}")
        else:
            print("No vote summary available.")
        
        # 6. Vote Summary by Party
        print("\n🏛️  VOTE SUMMARY BY PARTY:")
        print("-" * 35)
        
        party_query = text("""
            SELECT 
                c.party,
                COUNT(vt.vote_id) as vote_count
            FROM candidates c
            LEFT JOIN votes vt ON c.candidate_id = vt.candidate_id
            GROUP BY c.party
            ORDER BY vote_count DESC
        """)
        
        party_results = session.execute(party_query).all()
        
        if party_results:
            print(f"{'Party':<25} {'Votes':<8} {'Percentage':<12}")
            print("-" * 50)
            
            total_party_votes = sum(row[1] for row in party_results)
            
            for row in party_results:
                party = row[0]
                vote_count = row[1]
                percentage = (vote_count / total_party_votes * 100) if total_party_votes > 0 else 0
                
                print(f"{party:<25} {vote_count:<8} {percentage:.1f}%")
        else:
            print("No party-wise data available.")
        
        # 7. Database Statistics
        print("\n📈 DATABASE STATISTICS:")
        print("-" * 30)
        print(f"Total Voters: {len(voters_data)}")
        print(f"Total Candidates: {len(candidates_data)}")
        print(f"Total Votes Cast: {len(votes_data)}")
        
        if voters_data:
            voted_count = sum(1 for v in voters_data if v[4])
            turnout = (voted_count / len(voters_data) * 100) if voters_data else 0
            print(f"Voters Who Voted: {voted_count}")
            print(f"Voter Turnout: {turnout:.1f}%")
        
        print("\n" + "=" * 80)
        print("DATABASE VIEW COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    view_database()
