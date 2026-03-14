"""
Interactive Database Query Tool
Run custom SQL queries on your voting database
"""

from db import get_session
from sqlalchemy import text

def run_query(sql_query):
    """Execute a custom SQL query and return results"""
    try:
        with get_session() as session:
            result = session.execute(text(sql_query)).all()
            return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def interactive_query():
    print("🔍 INTERACTIVE DATABASE QUERY TOOL")
    print("=" * 50)
    print("Type your SQL queries below (or 'exit' to quit)")
    print("Available tables: voters, candidates, votes")
    print("-" * 50)
    
    while True:
        query = input("\n📝 Enter SQL query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
            
        print(f"\n🔄 Executing: {query}")
        print("-" * 40)
        
        result = run_query(query)
        
        if result:
            if len(result) == 0:
                print("📭 No results found.")
            else:
                # Print headers
                headers = result[0]._fields if hasattr(result[0], '_fields') else [f"Column {i+1}" for i in range(len(result[0]))]
                print(" | ".join(f"{header:<15}" for header in headers))
                print("-" * (len(headers) * 16))
                
                # Print data
                for row in result:
                    row_data = [str(getattr(row, header, row[i]) if hasattr(row, header) else row[i]) for i, header in enumerate(headers)]
                    print(" | ".join(f"{data:<15}" for data in row_data))
                
                print(f"\n📊 Total rows: {len(result)}")

# Pre-defined useful queries
def show_useful_queries():
    print("\n🎯 USEFUL PRE-DEFINED QUERIES:")
    print("-" * 40)
    print("1. Show all voters who voted:")
    print("   SELECT * FROM voters WHERE has_voted = 1")
    print("\n2. Show vote counts by candidate:")
    print("   SELECT c.name, c.party, COUNT(v.vote_id) as votes")
    print("   FROM candidates c LEFT JOIN votes v ON c.candidate_id = v.candidate_id")
    print("   GROUP BY c.candidate_id, c.name, c.party")
    print("\n3. Show who voted for whom:")
    print("   SELECT v.name as voter_name, c.name as candidate_name, c.party")
    print("   FROM voters v JOIN votes vt ON v.voter_id = vt.voter_id")
    print("   JOIN candidates c ON vt.candidate_id = c.candidate_id")
    print("\n4. Show voting statistics:")
    print("   SELECT")
    print("     COUNT(*) as total_voters,")
    print("     SUM(CASE WHEN has_voted = 1 THEN 1 ELSE 0 END) as voted_count,")
    print("     ROUND(SUM(CASE WHEN has_voted = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as turnout_percentage")
    print("   FROM voters")

if __name__ == "__main__":
    show_useful_queries()
    interactive_query()
